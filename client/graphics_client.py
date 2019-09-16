import socket
import struct
import sys
import os
class Client():

    def __init__(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, 3000))
        self.sock.settimeout(1000)
        
    def send_project(self, make_path):
        root_path = os.path.dirname(make_path)
        if os.path.exists(make_path):
            self.send_file(os.path.basename(make_path), make_path)
            for path, dirs, files in os.walk(root_path):
                for file in files:
                    filename = os.path.join(path,file)
                    relative_path = os.path.relpath(filename, root_path)
                    self.send_file(relative_path, filename)
            self.sock.send(b'end')
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        else:
            print('File path not found')


    def send_file(self, relative_path, full_path):
        header = struct.pack('<LL%ss' % len(relative_path), os.path.getsize(relative_path), len(relative_path), relative_path.encode())
        self.sock.send(header)
        with open(full_path, 'rb') as file_handle:
            self.sock.sendfile(file_handle)
        try:
            self.sock.recv(4096)
        except Exception as e:
            print('Failed to get acknowledgement', e)
        

def main():
    """Main Function."""
    client = Client(sys.argv[1])
    client.send_project(sys.argv[2])


if __name__ == "__main__":
    main()