#!/usr/bin/env python2.7

import socket
import sys
import subroutine


SMB_PORT = 445


def main(ip=subroutine.LOCAL_IP):
    # open rpc
    subroutine.log("Connecting to {}:{}".format(ip, SMB_PORT))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, 445))
    
    # create new file
    f = open ('test.exe', 'wb')
    subroutine.log('Created a new file %s' % f)
    
    # copy file from folder containing all DLLs --> System32
    subroutine.copy_file('C:\Windows\System32\MSPaint.exe', f)
    
    #client transfer file
    l = f.read(1024)
    while (l):
        s.send(l)
        l = f.read(1024)
    
    #server-side receiving code
    #while True:
    #    sc, address = s.accept()
    #
    #    print address
    #    i=1
    #    fi = open('','wb')
    #    i=i+1
    #    while (True):
    #        l = sc.recv(1024)
    #        while (l):
    #            fi.write(l)
    #            l = sc.recv(1024)
    #    fi.close()
    #
    #sc.close()
    subroutine.log("File Transfered")
    
    # close connection
    subroutine.log("Shutting down the conection...")
    s.close()
    subroutine.log("Closed connection to {}:{}".format(ip, SMB_PORT))
    
    # clear logs
    subroutine.clear_web_cache()


if __name__ == "__main__":
    exit(main())

