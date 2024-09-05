from . import utils
from common.constants import *
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
            if len(buf) == 0: # client disconnected
                return None

            bytes_to_recv -= len(buf)
            msg += buf
        
        return msg
    
    """
    Receives the message code through the socket.
    It returns None if the connection was closed
    """
    def receive_message_code(self):
        return self.recv_bytes(1)
    
    """
    Receives a message from a socket. It returns None if the client was desconnected
    when receiving the message.
    On success, it returns the bet
    """
    def receive_bet_message(self, client_id):
        bytes_to_recv = BET_LEN
        msg = self.recv_bytes(bytes_to_recv)
        if msg is None:
            return
        
        addr = self.client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

        bet = utils.process_bet_message(client_id, msg)
        return bet
    
    """
    Its receives a batch from the client. If there is a problem while receiveng, it returs false
    Otherwise, it return all the bets yaht were in the batch
    """
    def receive_batch(self, client_id):

        num_of_bets = self.recv_bytes(AMOUNT_OF_BETS_IN_BATCH_LEN)
        bets = []
        for _ in range (0, int(num_of_bets)):
            bet = self.receive_bet_message(client_id)
            if bet is None:
                return None
            bets.append(bet)
        return bets