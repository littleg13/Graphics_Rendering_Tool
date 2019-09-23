import socket
import struct
import subprocess
import os

class Server():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', 3000))
        self.sock.listen(5)
        self.client_sock = None

    def main_loop(self):
        starting_dir = os.getcwd()
        project = None
        while True:
            os.chdir(os.path.join(starting_dir, 'projects'))
            (client_sock, addr) = self.sock.accept()
            self.client_sock = client_sock
            if project is not None:
                del project
            project = Project(self.client_sock.recv(1024))
            self.client_sock.send(b'ack')
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
        self.client_sock.send(b'ack')
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
    def __init__(self, setup_packet):
        name_size, make_size, exec_size = struct.unpack_from('<LLL', setup_packet, 0)
        self.name, self.makefile, self.execfile = struct.unpack_from('<%ss%ss%ss' % (name_size, make_size, exec_size), setup_packet, 12)
        os.makedirs(self.name, exist_ok=True)
        os.chdir(self.name)
        self.process = None

    def __del__(self):
        self.process.terminate()
    
    def make(self):
        root_dir = os.getcwd()
        os.chdir(os.path.dirname(self.makefile))
        os.system('make')
        os.chdir(root_dir)

    def run(self):
        self.process = subprocess.Popen(self.execfile)
        
def main():
    """Main Function."""
    server = Server()
    server.main_loop()


if __name__ == "__main__":
    main()
