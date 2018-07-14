#!/usr/bin/python
'''
  Example:
  python console.py COM14 --sendfile=out.bin

  This file provides a simple console (using serial terminal), plus can do firmware upgrades and similar.
  
  WARNING: Do not send arbitrary files to ChipSHOUTER - it is designed to accept only specially signed
           firmware files.

  Copyright (c) 2017-2018 NewAE Technology Inc.
  All rights reserved.

'''
import time
import argparse
import threading
import sys
from chipshouter.console.serial_interface import Serial_interface
from chipshouter.console.download import cs_dl
try:
    from tqdm import tqdm
except Exception as e:
    print e

#sys.settrace
#---------------------------------------------------------------------------
class Console():
    def __init__(self, serial, threads = False, sendfile = '', verifyfile = ''):
        """ Initialze the console with the serial port passed in. """
        self.threads     = threads
        self.serial      = serial
        self.sendfile    = sendfile
        self.verifyfile  = verifyfile
        self.rx_callback = self.display_rx
        self.downloading = False
        self.rx_timer    = None
        self.menu = [
            {'input': '??',       'help' : 'Print this menu.',             'function' : self.print_menu   },

            {'input': 'sendfile', 'help' : 'Set / show file to download',  'function' : self.mod_sendfile },
            {'input': 'S',        'help' : 'Perform download of file: ',   'function' : self.download     },
            {'input': 'R',        'help' : 'Reset board: ',                'function' : self.reset        },
            {'input': 'quit',     'help' : 'Quit python app.',             'function' : self.quit         }
        ]
        self.stop = False
        self.process_receive()

    #---------------------------------------------------------------------------
    def mod_sendfile(self):
        """ This will reset the board .. used from the menu. """
        print 'Current file: ' + self.sendfile
        newfile = raw_input("Enter new relative filename: ")
        if len(newfile):
            self.sendfile = newfile
        print 'Console is now using: ' + self.sendfile

    #---------------------------------------------------------------------------
    def reset(self):
        """ This will reset the board .. used from the menu. """
        self.serial.s_write('reset \n')

    #---------------------------------------------------------------------------
    def process_receive(self):
        """ If this is not using threads This should be called on init to process receive. """
        if self.stop == True:
            self.rx_timer.cancel()
            return
        if self.threads:
            return
        while(self.serial.s_read()):
            continue
        self.rx_timer = threading.Timer(.1, self.process_receive)
        self.rx_timer.start()

    #---------------------------------------------------------------------------
    def print_menu(self):
        """ Prints the menu. """
        print "------------------------------------------------------------"
        print " The following SPECIAL COMMANDS are not sent to the         "
        print " ChipSHOUTER over the serial port, but are instead processed"
        print " by this Python application:                                 "
        for x in self.menu:
            print '    {:<10}'.format(x['input']) + '- ' + x['help']
        print "If none of these it will send to the board what you type."
        print "------------------------------------------------------------"

    #---------------------------------------------------------------------------
    def quit(self):
        """ Set the quit to know when to exit. """
        self.stop = True

    #---------------------------------------------------------------------------
    def display_rx(self, data):
        """ Display what was received, this is the intended callback for rx serial.
        """
        sys.stdout.write(data)

    #---------------------------------------------------------------------------
    def console(self):
        """ This is the main for the console this will get information from the
        user and execute the function that was in the menu. If there is no
        corresponding string, send the raw data to the shouter. """
        self.print_menu()
        self.serial.s_init(self.rx_callback)
        while not self.stop:
            send_to_shouter = True
            data = raw_input("")
            for x in self.menu:
                if x['input'] == data:
                    send_to_shouter = False
                    x['function']()
                    if self.stop:
                        return
            if send_to_shouter:
                self.serial.s_write(data + '\n')

    def test_frame(self):
        rval = self.download(break_frame = True)

    def test_crc(self):
        rval = self.download(break_crc = True)

    #---------------------------------------------------------------------------
    def verify(self):
        """ This will download the send file to the shouter. """
        print '*'*30
        print 'Stage 1 Downloading'
        print '*'*30
        if self.download(verify = True):
            print '*'*30
            print 'Stage 2 Downloading'
            print '*'*30
            checkstring = 'ChipShouter by NewAE Technology Inc.'
            rval = self.download(checkstring = checkstring)
            if checkstring in rval:
                print 'Good download'
            else:
                raise ValueError('Error App did not start')
                print 'Error with downloading file'
                print '*'*30
        else:
            raise ValueError('Error with downloading file')
            print 'Error with downloading file'
            print '*'*30

    #---------------------------------------------------------------------------
    def download(self, verify = False, checkstring = None, break_crc = False, break_frame = False):
        """ This will download the send file to the shouter. """

        # Check for verify if needed
        tempsendfile  = self.sendfile
        if verify:
            self.sendfile = self.verifyfile 

#        if self.rx_timer:
        self.rx_timer.cancel()

        print 'Sending: ' + self.sendfile
        if self.threads == True:
            dnld = cs_dl(self.serial.s_write)
        else:
            dnld = cs_dl(self.serial.s_write, wait_callback = self.serial.s_read )
        self.serial.s_init(dnld.rx_serial)

        filesize = dnld.get_file_size(self.sendfile)

        # Reset the board
        self.serial.s_write('s bb 0\n')
        print 'Setting download'
        self.serial.s_write('reset\n')

        response = dnld.wait_for_ack(10)
        print 'Done'
        if response != b'\x16':
            raise ValueError('Downloading did not receive response from the shouter')
            return

        packet = 0
        # Download the file
        try:
            for i in tqdm(range(filesize), ascii = True, desc = 'Downloading'):
                rval = dnld.send_packet(self.sendfile, packet, break_crc = break_crc, break_frame = break_frame)
                if rval == 0:
                    raise ValueError('Error with downloading file')
                    return '' 
                packet += 1
        except Exception as e:
            print e
            try:
                for i in range(filesize):
                    val_percent = i*100/filesize
                    sys.stdout.write('\r') #packet
                    sys.stdout.write( str(val_percent) + '%' + '#'*(val_percent / 10)) #packet
                    rval = dnld.send_packet(self.sendfile, packet, break_crc = break_crc, break_frame = break_frame)
                    if rval == 0:
                        raise ValueError('Error with downloading file')
                        return '' 
                    packet += 1
            except Exception as e:
                print 'download without tqdm'
                print e
                raise

            self.stop = True

        # Check for verify if needed
        if verify:
            ret = dnld.wait_for_ack(5)
            print 'Got someting' + ret 
            self.sendfile = tempsendfile
            if ret == b'\x1a':
                return True
            else:
                return False
        if checkstring:
            response = self.wait_for_string(checkstring, 18)
            return response

        self.serial.s_init(self.display_rx)
        self.process_receive()

    def wait_for_string(self, string, timeout):
        """ This will wait for a string to be received """
        oldtimeout = self.serial.s.timeout
        self.serial.s.timeout = 1 
        count = 0
        received = self.serial.s.readline()
        while string not in received:
            received = self.serial.s.readline()
            count += 1
            if count >= timeout:
                break
        return received
    pass

#--------------------------------------------------------------------------------
def main():
    """ This is the main entry for the console."""
    #----------------------------------------------------------------------------
    #--- Get the arguments
    parser = argparse.ArgumentParser(description='ChipSHOUTER serial interface console and firmware update application.',
    usage = sys.argv[0] + '[-h] port',  epilog='example: shouter-console.py COM114')
    parser.add_argument('port',          help='Serial port name')
    parser.add_argument('--sendfile',    help='Download file and wait in console [WARNING: causes firmware update on ChipSHOUTER].')
    parser.add_argument('--download',    help='Download file and exit console [WARNING: causes firmware update on ChipSHOUTER].')
    parser.add_argument('--checkstring', help='Check for specific string on startup.')
    parser.add_argument('--verify',      help='Test/Verify a download would work without doing actual upgrade.')
    parser.add_argument('--threads',     help='Option to use threads or not.')
    parser.add_argument('--test_crc',    help='Test a bad CRC (debug).')
    parser.add_argument('--test_frame',  help='Test a bad frame (debug).')
    args = parser.parse_args()

    sendfile = ''
    #-----------------------------------------------------------------------------
    #--- Get the args
    if args.port:
        port = args.port
    if args.download:
        sendfile = args.download
    if args.sendfile:
        sendfile = args.sendfile
    if args.threads:
        print 'Using threads'
        threads = True
        wait_callback = None
    else:
        threads = False

    # Initialize the Serial Interface
    serial = Serial_interface(use_threads = threads)

    # Open the port
    if serial.s_open(port, timeout = .01):
        print("Connected successful")
    else:
        print("Not connected")
        exit()

    # -------------------------------------------------------------------------
    if args.download and args.verify:
        my_console = Console(serial, threads = threads, sendfile = args.download, verifyfile = args.verify)
        my_console.verify()
        my_console.quit()
    elif args.verify:
        my_console = Console(serial, threads = threads, sendfile = args.download, verifyfile = args.verify)
        if my_console.download(verify = True) != True:
            raise ValueError('Did not verify')
        my_console.quit()
    elif args.download:
        my_console = Console(serial, threads = threads, sendfile = sendfile)
        if args.test_crc:
            my_console.test_crc()
        elif args.test_frame:
            my_console.test_frame()
        elif args.checkstring:
            print 'Checking for ' + args.checkstring
            rval = my_console.download(checkstring = args.checkstring)
            if args.checkstring not in rval:
                raise ValueError('Did not verify' + args.checkstring)
            my_console.quit()
        else:
            my_console.download()
            my_console.quit()
    else:
        my_console = Console(serial, threads = threads, sendfile = sendfile)
        my_console.console()

    time.sleep(1)
    serial.s_close()
    exit()

################################################################################
if __name__ == "__main__":
    main()
