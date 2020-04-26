import socket
import sys
import struct
import os
import time


def validate(addr):
    try:
        socket.gethostbyname(addr)
        return True
    except:
        return False



class UDPClient:
    def __init__(self, host, port, sock, command, buffer_size, default_filename):
        self.server_address = (host,port)
        self.sock = sock
        self.buffer_size = buffer_size
        self.command = command
        self.default_filename = default_filename

    def send_command(self):
        failed = True
        for i in range(3):
            success = self.send_command_once()
            if success:
                failed = False
                break
        if failed: #if fail 3 times
            print("Failed to send command. Terminating.", file=sys.stderr)
            self.sock.close()
            sys.exit(1)
        else:
            self.receive_file()

    def send_command_once(self):
        length = struct.pack('>H', len(self.command))
        self.sock.sendto(length, self.server_address)
        self.sock.sendto(self.command.encode(), self.server_address)
        # wait for ack
        self.sock.settimeout(1)
        try:
            receive_ack = (self.sock.recvfrom(3))[0]
            if receive_ack.decode() != 'ACK':
                return False
            return True
        except socket.timeout:
            return False

    def receive_file(self):
        #name file
        file_index = self.command.find('>')
        if file_index == -1:
            filename = self.default_filename
        else:
           # filename = command[file_index + 2:]
            command_array = self.command.split('>')
            filename = command_array[1].replace(' ', '')

        # remove file if already exists
        if os.path.exists(filename):
            os.remove(filename)

        #receive length
        length = (self.sock.recvfrom(bufferSize))[0]
        length = int.from_bytes(length, byteorder='big')

        with open(filename, 'a') as f:
            while True:
                # bytes_read  = sock.recv(buffer_size)
                success = False
                for i in range(3):
                    success, bytes_read = self.get_message()
                    if success:
                        #send ACK
                        self.sock.sendto('ACK'.encode(), self.server_address)
                        break
                    else:
                        time.sleep(1)
                if bytes_read == '':
                    break

                if not success:  # after 3 fails
                    self.sock.settimeout(None)
                    sys.exit()
                else:
                    f.write(bytes_read.decode())
        f.close()

        if length == os.path.getsize(filename):
            print("File %s saved." % filename)

    def get_message(self):
        self.sock.settimeout(0.5)
        try:
            message = (self.sock.recvfrom(bufferSize))[0]
            # message = message.decode()
            return True, message
        except socket.timeout:
            return False, ''


def run_script():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Enter server name or IP address:", end=" ")
    server_name = input()

    print("Enter port:", end=" ")
    port = int(input())

    if port < 0 or port > 65535:
        print("Invalid port number.", file=sys.stderr)
        sys.exit()

    if not validate(server_name):
        print("Could not connect to server.", file=sys.stderr)
        sys.exit()

    print("Enter command:", end=" ")
    command = input()
    # length = bytes([len(command)])
    #length = struct.pack('>H', len(command))

    client = UDPClient(server_name, port, sock, command, 512, 'response.txt')
    client.send_command()


if __name__ == '__main__':
    run_script()
