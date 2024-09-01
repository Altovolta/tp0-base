import socket
import logging

import signal
from . import utils, comunication as com

BETS_PER_BATCH = 5 #borrar

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
            bets = []
            cantidad_de_apuestas = 0
            while True:
                
                msg = com.recv_header(client_sock)

                if msg is None: #se desconecto el cliente
                    break
                
                if msg == com.BET_MESSAGE_CODE:
                    logging.debug("RECIBI BET CODE")
                    bet = com.receive_bet_message(client_sock)
                    bets.append(bet)
                elif msg == com.BATCH_END_CODE:
                    # falta manejar cuando hay error al procesar las bet del batch
                    utils.store_bets(bets)
                    cantidad_de_apuestas += len(bets)
                    logging.info(f"action: apuesta_recibida | result: success | cantidad: {cantidad_de_apuestas}")
                    bets = []
                    com.send_all(client_sock, "OK\n")
                elif msg == com.ALL_BETS_SENT_CODE:
                    logging.debug("ALL BETS WERE RECEIVED")
                    if len(bets) > 0:
                        utils.store_bets(bets)
                    break

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


