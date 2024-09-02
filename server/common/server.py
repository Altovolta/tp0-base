import socket
import logging

import signal
from . import server_protocol as pr, utils

NUM_DE_AGENCIAS = 5 #ponerlos en env var?

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.agencias_terminaron = 0
        self.sorteo_realizado = False
        self._got_close_signal = False
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:  
            client_sock = self.__accept_new_connection()
            if client_sock is None:
                break
            self.__handle_client_connection(client_sock)

            # if self.agencias_terminaron == NUM_DE_AGENCIAS:
            #     self.agencias_terminaron = 0
            #     logging.info("action: sorteo | result: success")
            #     self.__realizar_sorteo()
  
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        bets = []
        try:
            client_id = pr.recv_bytes(client_sock, 1)
            logging.debug(f"CLIENT {client_id} connected")

            while True: 
                msg = pr.recv_bytes(client_sock, 1)
                if msg is None: #se desconecto el cliente
                    break
                
                if msg == pr.BET_MESSAGE_CODE:
                    bet = pr.receive_bet_message(client_id, client_sock)
                    bets.append(bet)
                elif msg == pr.BATCH_END_CODE:
                    utils.store_bets(bets)
                    logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                    bets = []
                    pr.send_all(client_sock, "OK\n")
                elif msg == pr.ALL_BETS_SENT_CODE:
                    logging.debug("ALL BETS WERE RECEIVED")
                    self.client_finished()
                    break
                elif msg == pr.ASK_FOR_WINNERS:
                    if not self.sorteo_realizado:
                        pr.send_raffle_pending(client_sock)
                        break
                    pr.send_winners(client_sock, client_id)
                    break

        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
            pr.send_all(client_sock, "E\n")
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

    
    def client_finished(self):
        self.agencias_terminaron += 1
        if self.agencias_terminaron == NUM_DE_AGENCIAS:
            self.sorteo_realizado = True
            logging.info("action: sorteo | result: success")
        
    def sigterm_handler(self, signal, frame):
        logging.debug("Server socket closed")
        self._server_socket.close()
        self._got_close_signal = True


