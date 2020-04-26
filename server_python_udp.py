#https://pythontic.com/modules/socket/udp-client-server-example

import socket
import sys
import os
import struct
import time

ACK = "ACK".encode()


class UDPServer:
    def __init__(self, host, port, buffer_size, default_filename):
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((host, port))
        self.buffer_size = buffer_size
        self.default_filename = default_filename

    def receive_command(self):
        try:
            while (True):
                failed = True
                #command = ''
                #address = ''
                for i in range(3):
                    success = self.get_command()
                    if success:
                        # send ack
                        failed = False
                        #command = message
                        self.UDPServerSocket.sendto(ACK, self.address)
                        break
                    else:
                        # wait 1 sec
                        time.sleep(1)

                if failed:  # after 3 fails
                    print("Failed to receive instructions from the client.", file=sys.stderr)
                    self.UDPServerSocket.settimeout(None)
                else:
                    self.run_command()
        except KeyboardInterrupt:
            self.UDPServerSocket.close()
            sys.exit()

    def get_command(self):
        self.UDPServerSocket.settimeout(None)
        bytesAddressPair = self.UDPServerSocket.recvfrom(self.buffer_size)
        num_bytes = struct.unpack('>H', bytesAddressPair[0])
        self.address = bytesAddressPair[1]
        self.UDPServerSocket.settimeout(0.5)
        length = num_bytes[0]
        try:
            message_pair = self.UDPServerSocket.recvfrom(length)
            self.message = message_pair[0]
            if len(self.message) == length:
                return True
            else:
                print("Failed to receive instructions from the client.", file=sys.stderr)
                self.UDPServerSocket.settimeout(None)
                return False
        except socket.timeout:
            print("Failed to receive instructions from the client.", file=sys.stderr)
            self.UDPServerSocket.settimeout(None)
            return False

    def run_command(self):
        command = self.message.decode()
        file_index = command.find('>')
        if file_index == -1:
            self.filename = self.default_filename
            os.system(command + ' > ' + self.filename)
        else:
            command_array = command.split('>')
            self.filename = command_array[1].replace(' ', '')
            os.system(command)
        self.send_file()

    def send_file(self):
        file_size = os.path.getsize(self.filename)
        length = file_size.to_bytes(self.buffer_size, byteorder='big')
        self.UDPServerSocket.sendto(length, self.address)

        with open(self.filename, "rb") as f:
            while True:
                bytes_read = (f.read(self.buffer_size))
                if not bytes_read:
                    break
                failed = True
                for i in range(3):
                    success = self.send_message(bytes_read)
                    if success:
                        failed = False
                        break
                if failed:
                    print("File transmission failed.", file=sys.stderr)
                    self.UDPServerSocket.settimeout(None)
                    break
        f.close()

    def send_message(self, bytes):
            #sock.sendto(length, address)
            self.UDPServerSocket.sendto(bytes, self.address)
            # wait for ack
            self.UDPServerSocket.settimeout(1)
            try:
                receive_ack = (self.UDPServerSocket.recvfrom(3))[0]

                if receive_ack.decode() != 'ACK':
                    return False
                return True
            except socket.timeout:
                return False

def run_script():
    server_port = int(sys.argv[1])
    server = UDPServer('localhost', server_port, 512, 'outUDP.txt')
    server.receive_command()

if __name__ == '__main__':
    run_script()
