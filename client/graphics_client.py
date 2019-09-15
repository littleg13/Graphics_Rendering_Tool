import socket
import struct
import sys
import os
class Client():

    def __init__(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, 3000))
        

    def send_file(self, filepath):
        filename = os.path.basename(filepath).encode()
        header = struct.pack('<LL%ss' % len(filename), os.path.getsize(filepath), len(filename), filename)
        self.sock.send(header)
        with open(filepath, 'rb') as file_handle:
            file_handle
            self.sock.sendfile(file_handle)
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

def main():
    """Main Function."""
    client = Client(sys.argv[0])
    filepath = sys.argv[1]
    if os.path.exists(filepath):
        client.send_file(filepath)



if __name__ == "__main__":
    main()