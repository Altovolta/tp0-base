import socket
import logging

import signal
from . import utils
from common.constants import *
from common.server_protocol import *


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
        protocol = ServerProtocol(client_sock)
        bets = []
        try:
            client_id = protocol.recv_bytes(1)

            while True: 
                msg_code = protocol.receive_message_code()
                if msg_code is None: #client disconnected
                    break
                
                if msg_code == BATCH_MESSAGE_CODE:
                    if self.handle_batch_message(protocol, client_id) is None:
                        break
                elif msg_code == ALL_BETS_SENT_CODE:
                    self.handle_all_bets_sent_message()
                    #logging.debug(f"All bets from client {client_id} were received")
                    #self.client_finished()
                    break
                elif msg_code == ASK_FOR_WINNERS:
                    self.handle_winners_request_message(protocol, client_id)
                    # if not self.sorteo_realizado:
                    #     protocol.send_raffle_pending()
                    #     break
                    # protocol.send_winners(client_id)
                    # break

        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
            protocol.send_all("E\n")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            protocol.close()

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

    
    # def client_finished(self):
    #     self.agencias_terminaron += 1
    #     if self.agencias_terminaron == AMOUNT_OF_CLIENTS:
    #         self.sorteo_realizado = True
    #         logging.info("action: sorteo | result: success")
        
    def sigterm_handler(self, signal, frame):
        logging.debug("Server socket closed")
        self._server_socket.close()
        self._got_close_signal = True

###########################################################
    def handle_batch_message(self, protocol:ServerProtocol, client_id):
        bets = protocol.receive_batch(client_id)
        if bets is None:
            return
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
        utils.store_bets(bets)
        if protocol.send_all(BATCH_RECEIVED_SUCCESS) == 0:
            return None
        return True

    def handle_all_bets_sent_message(self):

        self.agencias_terminaron += 1
        if self.agencias_terminaron == AMOUNT_OF_CLIENTS:
            #obtengo los ganadores aca?
            self.sorteo_realizado = True
            logging.info("action: sorteo | result: success")

    def handle_winners_request_message(self, protocol:ServerProtocol, client_id):
        if not self.sorteo_realizado:
            protocol.send_raffle_pending()
            return False
        
        winners = utils.get_winners(client_id)
        protocol.send_winners(winners)
        return True