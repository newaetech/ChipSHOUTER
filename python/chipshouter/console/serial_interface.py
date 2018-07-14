#!/usr/bin/env python

#---------------------------------------------------------------------------
"""
This is the file to handle the serial interfaces. 
"""
#---------------------------------------------------------------------------

import Queue
from threading import Thread
import serial
import serial.tools.list_ports

class Serial_interface(object):
    def __init__(self, use_threads = True):
        self.use_thread     = use_threads
        self.s              = serial.Serial()
        self.__quit         = False
        self.__hijacked_cb  = None
        self.__rx_callback  = None 

        if self.use_thread:
            self.__rx_queue = Queue.Queue() 
            print 'Starting serial with threads'

    def __thread_run_rx(self):
        """ This will scan the quit attribute to see  if we need to disconnect and 
        stop the thread.
        
        When serial data is received it will: Write the data to the queue that
        was initialized on the start of the 
        __init__ 
        """
        print('Running RX')
        while self.__quit == False:
            while self.s.is_open:
                try:
                    read_data = ''
                    read_data += self.s.read()
                    while(self.s.inWaiting() > 0):
                        read_data += self.s.read()

                    if read_data != '':
                        self.__rx_queue.put(read_data)
                    
                    if self.__quit == True:
                        print("Exiting serial Thread because I was told")
                        break
                except:
                    if self.__quit == True:
                        print("Exiting serial Thread because I was had to")
                        break

    def __thread_run_rx_app_handle(self):
        """  This will be run by the thread after start is called.
        """
        print('Running APP handler')
        while not self.__quit:
            # Get all the data from the queue
            while self.__rx_queue.qsize():
                try:
                    read_data = self.__rx_queue.get()
                    # Call the callback function for processing
                    try:
                        if self.__rx_callback:
                            self.__rx_callback(read_data)
                    except Exception as e: 
                        print(e)
                        print("Bad callback in rx")
                except Queue.Empty:
                    pass
            time.sleep(.02)
        print("Exiting serial_rx Thread because I was told")

    def s_list_ports(self):
        """ List the available com ports and returns the list of them to choose.
        """
        ports = serial.tools.list_ports.comports()
        s_ports = [] 
        for x  in ports:
            s_ports.append(str(x.device))
        return s_ports

    def s_init(self, rx_callback):
        """ Initializes the serial interface.
        """

        self.__rx_callback = rx_callback

    def s_hijack_receive(self, rx_callback):
        """ Initializes the serial interface.
        """
        if self.__hijacked_cb == None:
            self.__hijacked_cb = self.__rx_callback;
        self.__rx_callback = rx_callback

    def s_return_receive(self):
        """ Initializes the serial interface.
        """
        if self.__hijacked_cb != None:
            self.__rx_callback = self.__hijacked_cb 
            self.__hijacked_cb = None 

    def s_open(self, port, timeout = .1):
        """ Open the serial interface. Returns True if the opened or False if not.
        """

        connected = False
        try:
            self.s = serial.Serial(
                timeout = timeout,
                port = port,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.EIGHTBITS
            ) 
            connected = True
            self.s.flushInput()
            self.s.flushOutput()
            if self.use_thread:
                #--- Start the Serial port
                self.__quit = False
                self.__serial_rx_thread             = Thread(target = self.__thread_run_rx)
                self.__serial_rx_app_handle_thread  = Thread(target = self.__thread_run_rx_app_handle)

                self.__serial_rx_thread.start()
                self.__serial_rx_app_handle_thread.start()
            
        except Exception as err:
            print err
            connected = False
        return(connected)

    def s_close(self):
        """
        Close the serial interface.
        
        Returns - The open state of the port. True if connected otherwise false
        """

        # If threaded close and
        self.__quit = True

        if self.s.is_open:
            self.s.close()
        return False

    def s_write(self, data):
        """
        Write data to the serial interface.
        
        Returns
        -------
        bool 
        True if the opened.
        False if not opened.
        """
        if self.s.is_open:
            try:
                self.s.write(data)
            except:
                print("Could not write to port")
        else:
            raise IOError('Comport is not open, use ctl_connect()')

    def s_read(self, timeout = 0):
        """
        Read data from the serial interface.
        
        Returns
        -------
        bytes read.

        """
        if self.s.is_open:
            try:
                data = self.s.read(100)
                # Call the callback function for processing
                try:
                    if self.__rx_callback:
                        self.__rx_callback(data)
                except Exception as e: 
                    print(e)
                    print("Bad callback in rx")
                return data
            except:
                print("Could not read from port")
        else:
            raise IOError('Comport is not open, use ctl_connect()')


#-----------------------------------------------------------------------------#
#--- Main --------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
import sys
def test_rx(data):
    sys.stdout.write(data)
    pass

import argparse
import time

user_input = ''
def scan_input():
    global user_input
    while True:
        user_input = raw_input("scan_input:")
        if user_input == 'quit':
            print 'Got quit exiting'
            break
    pass

def get_user_input():
    global user_input
    rvalue = user_input
    user_input = ''
    return rvalue 

def main():
    #----------------------------------------------------------------------------
    #--- Get the arguments
    parser = argparse.ArgumentParser(description='Chipshouter test program')
    parser.add_argument('port', help='comport')
    parser.add_argument('--sendfile', help='download file')
    args = parser.parse_args()

    #-----------------------------------------------------------------------------
    #--- Set the args
    sendfile = 'out.bin'
    if args.port:
        port = args.port
    if args.sendfile:
        sendfile = args.sendfile

    #----------------------------------------------------------------------------
    #--- Start the Shouter API 
    data = raw_input("Yes for threading Otherwise select no:")
    if data.lower() == 'yes':
        print '-------------------------'
        print 'Testing Threading version'
        print '-------------------------'
        st = Serial_interface()
        st.s_init(test_rx)
        if st.s_open(port) == True:
            print 'Connected to comport:'
            data = ''
            while True:
                data = raw_input("")
                if data == 'quit':
                    break
                st.s_write(data)
                st.s_write('\n')
            st.s_close()
        else:
            print 'Can not Connect:'
    else:
        print '-------------------------'
        print 'Testing NON Threading version'
        print '-----------------------------'
        st = Serial_interface(use_thread = False)
        st.s_init(test_rx)
        if st.s_open(port) == True:
            print 'Connected to comport:'
            data = ''
            input_thread  = Thread(target = scan_input)
            input_thread.start()
            print 'Wait for input:'

            #--------------------------------
            while True:
                data = get_user_input()
                if len(data):
                    if data == 'quit':
                        break
                    print 'Writing data: ' + data
                    st.s_write(data)
                    st.s_write('\n')
                else:
                    time.sleep(.1)
                    while len(st.s_read()):
                        pass
            #--------------------------------
            st.s_close()
        else:
            print 'Can not Connect:'
        pass


    time.sleep(1)
    exit()

################################################################################
#
if __name__ == "__main__":
    main()
