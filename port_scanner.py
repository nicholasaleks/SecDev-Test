# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

target = input('What website to scan?: ')
inidcator = 0
def pscan(port):
    try:
    
        con = s.connect((target,port))
        return True
    except:
        return False

num =10;
def check(port_num):
      if pscan(port_num):
           print('Port',port_num,'is open')
           exit()
      else: 
           print('Port',port_num,'is not open')

for x in range(num):
    check(x)
while inidcator == 0:
    dport = int(input("Please enter any port number to try: or enter alphabet to exit"));
    check(dport)
        
        