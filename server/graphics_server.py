import socket
import struct
import os

class Server():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', 3000))
        self.sock.listen(5)
        self.client_sock = None

    def main_loop(self):
        while True:
            (client_sock, addr) = self.sock.accept()
            self.client_sock = client_sock
            self.recv_file()
            

    def recv_file(self):
        header = self.client_sock.recv(4096)
        size, name_length = struct.unpack_from('<LL', header, 0)
        filename = struct.unpack_from('<%ss' % name_length, header, 8)[0]
        print(filename.decode())
        print(size)
        data_recv = 0
        with open(filename, 'wb') as file_handle:
            while data_recv < size:
                try:
                    data = self.client_sock.recv(4096)
                    data_recv += len(data)
                    file_handle.write(data)
                except Exception as e:
                    print(e)
                    break 
        os.startfile(filename)

def main():
    """Main Function."""
    server = Server()
    server.main_loop()


if __name__ == "__main__":
    main()