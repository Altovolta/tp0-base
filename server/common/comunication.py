from . import utils
import logging

def receive_batch(client_socket, bets_per_batch):
    bets = []

    for _ in range(0, bets_per_batch):
        msg = receive_message(client_socket)
        if msg is None: 
            return None #ver que hacer aca

        # addr = client_socket.getpeername()
        # logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
        bet = process_message(msg) # puede haber error? -> solo si me mandan mal el mensaje
        bets.append(bet)
    return bets


def process_message(msg):
    id_agencia = msg[0]
    name_len = int(msg[1:3])
    name = msg[3:3 + name_len]
    apellido_len = int(msg[26:28])
    apellido = msg[28:28 + apellido_len]
    dni = msg[38:46]
    fecha_nac = msg[46:56]
    numero = msg[56:]
    return utils.Bet(id_agencia, name, apellido, dni, fecha_nac, numero)


"""
Receives a message from a socket. It returns None if the client was desconnected
when receiving the message.
On success, it returns the message
"""
def receive_message(client_socket):
    bytes_to_recv = 60
    msg = ""

    while bytes_to_recv > 0:

        buf = client_socket.recv(bytes_to_recv).rstrip().decode('utf-8')

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