import json
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
        starting_dir = os.getcwd()
        while True:
            os.chdir(os.path.join(starting_dir, 'projects'))
            (client_sock, addr) = self.sock.accept()
            self.client_sock = client_sock
            project = Project(self.recv_file())
            while self.recv_file() is not None:
                continue
            project.make()
            project.run()

            
    def recv_file(self):
        header = self.client_sock.recv(4096)
        if header == b'end':
            return None
        size, name_length = struct.unpack_from('<LL', header, 0)
        filename = struct.unpack_from('<%ss' % name_length, header, 8)[0]
        if len(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
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
        self.client_sock.send(b'ack')
        return filename


class Project():
    def __init__(self, make_path):
        with open(make_path, 'rb') as renderMake:
            self.renderMake = json.load(renderMake)
        self.name = self.renderMake['name']
        self.makefile = self.renderMake['makefile']
        self.execfile = self.renderMake['exec']
        os.makedirs(self.name, exist_ok=True)
        os.chdir(self.name)

    def make(self):
        os.system(self.makefile)

    def run(self):
        os.system(self.execfile)
        
def main():
    """Main Function."""
    server = Server()
    server.main_loop()


if __name__ == "__main__":
    main()