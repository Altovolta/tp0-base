import socket
import logging

import signal
from . import utils, comunication as com

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        
        self._got_close_signal = False
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while True:  
            client_sock = self.__accept_new_connection()
            if client_sock is None:
                break
            self.__handle_client_connection(client_sock)

            

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = com.receive_message(client_sock)
            if msg is None: 
                client_sock.close()
                return 

            bet = self.process_message(msg)
            utils.store_bets([bet]) 
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")

            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

            com.send_all(client_sock, "OK\n")

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        try:
        # Connection arrived
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if not self._got_close_signal:
                logging.critical(f"action: accept_connections | result: fail | error: {e}")
            
        
    def sigterm_handler(self, signal, frame):
        logging.debug("Server socket closed")
        self._server_socket.close()
        self._got_close_signal = True

    def process_message(self, msg):
        id_agencia = msg[0]
        name_len = int(msg[1:3])
        name = msg[3:3 + name_len]
        apellido_len = int(msg[26:28])
        apellido = msg[28:28 + apellido_len]
        dni = msg[38:46]
        fecha_nac = msg[46:56]
        numero = msg[56:]

        #logging.debug(f"id: {id_agencia} | n_len: {name_len} | name: {name} | a_len: {apellido_len} | apell: {apellido} | dni: {dni} | nac: {fecha_nac} | num: {numero}")

        return utils.Bet(id_agencia, name, apellido, dni, fecha_nac, numero)
