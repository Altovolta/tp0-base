from common.constants import *

class ServerProtocol:

    def __init__(self, client_socket):
        self.client_sock = client_socket

    def close(self):
        self.client_sock.close()

    """
    Receives a message from a socket. It returns None if the client was desconnected
    when receiving the message.
    On success, it returns the message
    """
    def receive_message(self):
        bytes_to_recv = BET_LEN
        msg = ""

        while bytes_to_recv > 0:

            buf = self.client_sock.recv(bytes_to_recv).rstrip().decode('utf-8')

            if len(buf) == 0: # client disconnected
                return None

            bytes_to_recv -= len(buf)
            msg += buf
        
        return msg

    """
    Sends a message through the socket. It returns 0 if the message wasn't sent
    On success, it returns the ammount of bytes sent
    """
    def send_all(self, msg):

        bytes_to_send = len(msg)
        bytes_sent = 0

        while bytes_to_send > bytes_sent:
            n = self.client_sock.send(msg[bytes_sent:].encode('utf-8'))
            if n == 0: # client disconnected
                return 0
            bytes_sent += n

        return bytes_sent