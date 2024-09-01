from . import utils
import logging

BET_MESSAGE_CODE = "0"
BATCH_END_CODE = "1"
ALL_BETS_SENT_CODE = "2"

"""
Receives a message from a socket. It returns None if the client was desconnected
when receiving the message.
On success, it returns the message
"""

def recv_header(socket):
    return recv_bytes(socket, 1)

def receive_bet_message(client_socket):
    bytes_to_recv = 60
    msg = recv_bytes(client_socket, bytes_to_recv)
    if msg is None:
        return
    bet = utils.process_bet_message(msg)
    return bet

def recv_bytes(socket, bytes_to_recv):
    msg = ""

    while bytes_to_recv > 0:

        buf = socket.recv(bytes_to_recv).rstrip().decode('utf-8')

        if len(buf) == 0: # client disconnected
            return None

        bytes_to_recv -= len(buf)
        msg += buf
    
    return msg

"""
Sends a message through the socket. It returns 0 if the message wasn't sent
On success, it returns the ammount of bytes sent
"""
def send_all(socket, msg):

    bytes_to_send = len(msg)
    bytes_sent = 0

    while bytes_to_send > bytes_sent:
        n = socket.send(msg[bytes_sent:].encode('utf-8'))
        if n == 0: # client disconnected
            return 0
        bytes_sent += n

    return bytes_sent