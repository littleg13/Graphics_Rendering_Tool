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
        size, name_length, modified_time, accessed_time = struct.unpack_from('<LLff', header, 0)
        filename = struct.unpack_from('<%ss' % name_length, header, 16)[0]
        if os.path.exists(filename) and os.stat(filename).st_mtime == modified_time:
            self.client_sock.send(b'deny')
            return False
        else:
            self.client_sock.send(b'accept')
        
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
        os.utime(filename, (accessed_time, modified_time))
        return filename


class Project():
    def __init__(self, setup_packet):
        name_size, make_size, exec_size, arg_size = struct.unpack_from('<LLLL', setup_packet, 0)
        self.name, self.makefile, self.execfile, self.arguments = struct.unpack_from('<%ss%ss%ss%ss' % (name_size, make_size, exec_size, arg_size), setup_packet, 16)
        arguments = self.arguments.split()
        for arg in self.arguments.split():
            if arg == b'-c' or arg == b'--clean':
                print(os.getcwd())
                os.system('rm -rf ./*')
                arguments.remove(arg)
                break
        self.arguments = b' '.join(arguments)
        os.makedirs(self.name, exist_ok=True)
        os.chdir(self.name)
        if os.path.exists(self.execfile):
            print(os.getcwd())
            os.system('rm %s' % self.execfile.decod())
        self.process = None

    def __del__(self):
        if self.process is not None:
            self.process.terminate()
    
    def make(self):
        root_dir = os.getcwd()
        os.chdir(os.path.dirname(self.makefile))
        subprocess.call('make', shell=True)
        os.chdir(root_dir)

    def run(self):
        root_dir = os.getcwd()
        os.chdir(os.path.dirname(self.execfile))
        if os.path.isfile(os.path.basename(self.execfile.decode())):
            self.process = subprocess.Popen('exec ./' + os.path.basename(self.execfile.decode()) + ' ' + self.arguments.decode(), shell=True)
        os.chdir(root_dir)
        
def main():
    """Main Function."""
    absPath = os.path.abspath(__file__)
    dirName = os.path.dirname(absPath)
    os.chdir(dirName)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print('IP: ' + s.getsockname()[0])
    s.close()
    server = Server()
    server.main_loop()


if __name__ == "__main__":
    main()
