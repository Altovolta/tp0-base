from . import utils
import logging
from common.constants import *

class ServerProtocol:

    def __init__(self, client_socket):
        self.client_sock = client_socket

    def close(self):
        self.client_sock.close()

    
    def send_all(self, msg):
        """
        Sends a message through the socket avoiding short writes. It returns 0 if the message wasn't sent
        On success, it returns the ammount of bytes sent
        """
        bytes_to_send = len(msg)
        bytes_sent = 0

        while bytes_to_send > bytes_sent:
            n = self.client_sock.send(msg[bytes_sent:].encode('utf-8'))
            if n == 0: # client disconnected
                return 0
            bytes_sent += n

        return bytes_sent

    
    def recv_bytes(self, bytes_to_recv):
        """
        Receives a message through the socket avoiding short reads. 
        It returns None if the connection was closed. Otherwise, it returns the message
        """
        msg = ""

        while bytes_to_recv > 0:

            buf = self.client_sock.recv(bytes_to_recv).rstrip().decode('utf-8')
            if len(buf) == 0: # client disconnected
                return None

            bytes_to_recv -= len(buf)
            msg += buf
        
        return msg
    
    def receive_message_code(self):
        """
        Receives the message code through the socket.
        It returns None if the connection was closed
        """
        return self.recv_bytes(1)

    def receive_bet_message(self, client_id):
        """
        Receives a message from a socket. It returns None if the client was desconnected
        when receiving the message.
        On success, it returns the bet
        """
        bytes_to_recv = BET_LEN
        msg = self.recv_bytes(bytes_to_recv)
        if msg is None:
            return
        
        addr = self.client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

        bet = utils.process_bet_message(client_id, msg)
        return bet
    
    def receive_batch(self, client_id):
        """
        Its receives a batch from the client. If there is a problem while receiveng, it returs false
        Otherwise, it return all the bets yaht were in the batch
        """
        num_of_bets = self.recv_bytes(AMOUNT_OF_BETS_IN_BATCH_LEN)
        bets = []
        for _ in range (0, int(num_of_bets)):
            bet = self.receive_bet_message(client_id)
            if bet is None:
                return None
            bets.append(bet)
        return bets
    
    def send_raffle_pending(self):
        """
        Sends that the raffle is still pending through the socket.
        It returns 0 if there was an error while sending
        """
        return self.send_all(RAFFLE_PENDING)
    
    def send_raffle_ready(self):
        """
        Sends that the raffle is ready through the socket.
        It returns 0 if there was an error while sending
        """
        return self.send_all(RAFFLE_READY)
    
    def send_winners(self, winners):
        """
        Sends the raffle winners through the socket.
        It returns 0 if there was an error while sending
        """
        status = self.send_raffle_ready()
        if status == 0:
            return 0
        for winner in winners:
            msg = winner.document + "\n"
            if self.send_all(msg) == 0:
                return 0

        return self.send_all(ALL_WINNERS_SENT)
    