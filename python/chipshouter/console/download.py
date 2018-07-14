import sys
import time
from binascii import hexlify

class cs_buffer():
    """ Buffering for the packets received during downloading. """
    def __init__(self):
        self.__rx_buffer = []

    def get_num_rx(self):
        """ Add packet to buffer """
        return(len(self.__rx_buffer))

    def add(self, packet):
        """ Add packet to buffer """
        if len(packet):
            self.__rx_buffer.append(packet)

    def clear(self):
        self.__rx_buffer = []
    
    def find(self, match):
        """ Get the oldest packet """
        if len(self.__rx_buffer) == 0:
            return [] 
        item = 0 
        for x in self.__rx_buffer:
            if x.find(match) == 0:
                del(self.__rx_buffer[item])
                return x 
            item = item + 1
        return []

        packet = self.peek()
        if len(packet):
            # Delete the read packet
            self.__rx_buffer = self.__rx_buffer[1:]
            return packet

    def get(self):
        """ Get the oldest packet """
        packet = self.peek()
        # Delete the read packet
        self.__rx_buffer = self.__rx_buffer[1:]
        return packet

    def peek(self):
        """ Get the oldest packet Without deleting """
        if len(self.__rx_buffer):
            return(self.__rx_buffer[0])
        return []
    
    def get_buffer(self):
        return self.__rx_buffer

################################################################################
#  Serial Download class
class cs_dl():
    """ cs_dl() This handles the sending of the file to the chip shouter.
     1. You need to pass in a method to transmitt the data.
     2. You also need to call cs_dl.rx_serial when data is received.

        Sample of the initialization using the serial_thread.py:

        # Start the Serial port
        queue = Queue.Queue()
        myserial = serial_thread(queue)

        # Init the seriel download and give it a method to transmitt the data.
        dnld = cs_dl(myserial.tx)
        # Set the receive to be the serial_dnld.rx_serial
        rx_serial = serial_rx_thread(queue, dnld.rx_serial)

    """
    def __init__(self, cb_tx, wait_callback = None, use_threads = False):
        self.buff = cs_buffer()

        self.__rx_buffer = bytearray()
        self.__wait_callback = wait_callback
        self.__use_threads = use_threads 

        self.__binary_mode       = False
        self.__cb_tx             = cb_tx         # Callback for the transmission

        self.__print_rx          = False
        self.__print_rx_details  = False

    #---------------------------------------------------------------------------
    def set_print_rx(self, state):
        self.__print_rx = state
    def set_print_rx_details(self, state):
        self.__print_rx_details = state

    #---------------------------------------------------------------------------
    def wait_for_ack(self, timeout):
        """ Wait for an ack
        Returns the __thread_rx_command
        """
        timeout_multiplier = 100
        if self.__use_threads:
            timeout_multiplier = 100

        check_commands = [  b'\x15', #self.shout_dnld.dl_cmd_ack,
                            b'\xff', #self.shout_dnld.dl_cmd_nack,
                            b'\xfe', #self.shout_dnld.dl_cmd_framming_error,
                            b'\xfc', #self.shout_dnld.dl_cmd_timeout,
                            b'\x16', #self.shout_dnld.dl_cmd_boot_start
                            b'\x1a'  #self.shout_dnld.dl_cmd_boot_start
        ]

        timeout_count = 0
        while timeout_count < (timeout * timeout_multiplier):
#            print 'Wait ... ' + str(timeout_count) + ' : ' + str(timeout * 100) 
            # Call this callback if you need something to do like recieve for non threaded applications.
            if self.__wait_callback:
                self.__wait_callback()
            for x in check_commands:
                if self.buff.get_num_rx():
                    if len(self.buff.find(x)):
                        self.buff.clear()
                        return x
            time.sleep(.01)
            timeout_count = timeout_count + 1
        return b'\x00'

    #---------------------------------------------------------------------------
    def file_get(self, my_file):
        """ reads a file into a list
        """
        try:
            f = open(my_file, "rb")
        except:
            print("Error opening " + my_file)
            return ''
        try:
            byte = f.read(1)
            data = ''
            while byte != "":
                data = data + byte
                byte = f.read(1)
        finally:
            f.close()
        return data

    def get_file_size(self, filename):
        ''' Gets the number of packets in the file for downloading '''
        file_tx = self.file_get(filename)
        packets = 0
        try:
            end = file_tx.find('\x7f') + 1
        except Exception as e:
            print 'Error with the file'
            print e
            return 0
        while end > 0:
            packets += 1
            file_tx = file_tx[end:]
            end = file_tx.find('\x7f') + 1
        return packets

    def send_packet(self, filename, packet, break_crc = False, break_frame = False):
        file_tx       = self.file_get(filename)
        end           = 0
        packet_count  = 0

        # Get the first packet
        end   = file_tx.find('\x7f') + 1
        start = file_tx.find('\x7e')
        tx_packet = file_tx[start:end]
        # bread_crc
        if break_crc:
            tx_packet = tx_packet[:-2]
            tx_packet += b'\xa8\x7f'
        # bread_frame
        if break_frame:
            tx_packet = tx_packet[:-1]
            tx_packet += b'\x7f'

        # Find the packet # to send
        while end > 0 and start >= 0 :
            if packet == packet_count:
                retry = 0
                while retry < 5:
                    self.__cb_tx(tx_packet)
                    # Wait seconds for an ack
                    response = self.wait_for_ack(1)
                    if response == b'\x15': #self.shout_dnld.dl_cmd_ack:
                        return len(tx_packet)
                    else:
                        retry = retry + 1
                return 0
            else:
                packet_count += 1
                # Get the next packet
                file_tx = file_tx[end:]
                end     = file_tx.find('\x7f') + 1
                start   = file_tx.find('\x7e')
                tx_packet = file_tx[start:end]
        print 'Returning'
        return 0

    #---------------------------------------------------------------------------
    def packet_unstuff(self, data):
        """ remove the special characters for stuffing 
        """
        unstuffed = bytearray()
        escape = False
         
        for count in data:
            if escape == False:
                if count == 0x7e:
                    continue
                if count == 0x7f:
                    continue 
                if count == 0x7d:
                    escape = True
                else:
                    unstuffed.append(count)
            else:
                unstuffed.append(count + 0x7d)
                escape = False

        return(unstuffed)

    #---------------------------------------------------------------------------
    def rx_serial(self, data):
        """ rx_serial will handle all the received data.
        This should be called from some serial receive.
        """
        if self.__print_rx_details:
            if len(data):
                print 'rx: ' + hexlify(data)

        # This -----------------------------------------------------------------
        # Copy received to the buffer.
        self.__rx_buffer = self.__rx_buffer + bytearray(data)

        start = self.__rx_buffer.find('\x7e')
        end   = self.__rx_buffer.find('\x7f')

        # If not found clear the buffer and wait for it.
        if start < 0:
            self.__rx_buffer = bytearray()
            return
        # If no end not found... wait for more.
        if end < 0:
            return

        # Get the frames
        while start < end:
            start = self.__rx_buffer[:end].rfind('\x7e')
            self.buff.add(self.packet_unstuff(self.__rx_buffer[start:end + 1]))
            if self.__print_rx:
                print("PACKET!!: " + hexlify(self.__rx_buffer[start:end + 1]))

            self.__rx_buffer = self.__rx_buffer[end + 1:]
            start = self.__rx_buffer.find('\x7e')
            end   = self.__rx_buffer.find('\x7f')
            if start < 0:
                self.__rx_buffer = bytearray()
                return
        return
