from . import utils
import logging

class ServerProtocol:

    def __init__(self, client_socket):
        self.client_sock = client_socket

    def close(self):
        self.client_sock.close()

    """
    Sends a message through the socket avoiding short writes. It returns 0 if the message wasn't sent
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

    """
    Receives a message through the socket avoiding short reads. 
    It returns None if the connection was closed. Otherwise, it returns the message
    """
    def recv_bytes(self, bytes_to_recv):
        msg = ""

        while bytes_to_recv > 0:

            buf = self.client_sock.recv(bytes_to_recv).rstrip().decode('utf-8')
            logging.debug(f"ESTOY LEYENDO: {buf} y SU LEN ES {len(buf)}")
            if len(buf) == 0: # client disconnected
                return None

            bytes_to_recv -= len(buf)
            msg += buf
        
        return msg
    
    def receive_message_code(self):
        return self.recv_bytes(1)
    
    """
    Receives a message from a socket. It returns None if the client was desconnected
    when receiving the message.
    On success, it returns the bet
    """
    def receive_bet_message(self):
        bytes_to_recv = 60
        msg = self.recv_bytes(bytes_to_recv)
        if msg is None:
            return
        
        addr = self.client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

        bet = utils.process_bet_message(msg)
        return bet