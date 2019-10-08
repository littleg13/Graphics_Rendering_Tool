import socket
import struct
import sys
import os
class Client():

    def __init__(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, 3000))
        self.sock.settimeout(5)
        
    def send_project(self, root_path, make_path, exec_path, arguments):
        if os.path.exists(root_path):
            name = os.path.basename(root_path)
            pack_str = '<LLLL{name_size}s{make_size}s{exec_size}s{optional_size}s'.format(
                name_size=len(name),
                make_size=len(make_path),
                exec_size=len(exec_path),
                optional_size=len(arguments)
                )
            data = struct.pack(pack_str, len(name), len(make_path), len(exec_path), len(arguments), name.encode(), make_path.encode(), exec_path.encode(), arguments.encode())
            self.sock.send(data)
            try:
                if self.sock.recv(4096) == b'ack':
                    print('recieved ack for project setup')
            except Exception as e:
                print('Failed to get acknowledgement', e)
            for path, dirs, files in os.walk(root_path):
                for file in files:
                    filename = os.path.join(path,file)
                    if '.py' not in file:
                        relative_path = os.path.relpath(filename, root_path)
                        self.send_file(relative_path, filename)
            self.sock.send(b'end')
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        else:
            print('File path not found')

    def send_file(self, relative_path, full_path):
        header = struct.pack('<LL%ss' % len(relative_path), os.path.getsize(full_path), len(relative_path), relative_path.encode())
        self.sock.send(header)
        try:
            if self.sock.recv(4096) == b'ack':
                print('recieved ack for %s' % relative_path)
        except Exception as e:
            print('Failed to get acknowledgement', e)
        with open(full_path, 'rb') as file_handle:
            print(self.sock.sendfile(file_handle))
        try:
            if self.sock.recv(4096) == b'ack':
            	print('recieved ack for %s' % relative_path)
        except Exception as e:
            print('Failed to get acknowledgement', e)

        

def main():
    """Main Function."""
    print(sys.argv)
    client = Client(sys.argv[1])
    client.send_project(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


if __name__ == "__main__":
    main()
