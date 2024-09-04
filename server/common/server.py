import socket
import logging

import signal
from . import server_protocol as pr, utils, client_handler as ch
from multiprocessing import Process, Lock, Value, Manager
NUM_DE_AGENCIAS = 5 #ponerlos en env var?

BET_MESSAGE_CODE = "0"
BATCH_END_CODE = "1"
ALL_BETS_SENT_CODE = "2"
ASK_FOR_WINNERS = "3"

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.agencias_terminaron = Value('i', 0)#indica cuantas agencias terminaron su envio
        self.file_lock = Lock() 
        self.manager = Manager()
        self.winners = self.manager.list()
        self.sorteo_realizado =  Value('i', 0)#False
        self._got_close_signal = False
        self._clients_handles = []
        self.clients = []
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
                #joineo los threads?
                break
            self.__handle_client_connection(client_sock)

  
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        protocol = pr.ServerProtocol(client_sock)
        cli_id = protocol.recv_bytes(1)
        if cli_id is None:
            protocol.close()
            return
        client_handler = ch.ClientHandler(protocol, int(cli_id), self.file_lock, self.agencias_terminaron, self.winners, self.sorteo_realizado)
        self.clients.append(client_handler) #para cerrar los socket?
        p = Process(target=client_handler.run, args=())
        p.start()
        self._clients_handles.append(p)

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
        self._got_close_signal = True
        self._server_socket.close()
        for client in self.clients:
            client.stop()
        for handle in self._clients_handles:
            handle.join()
        # ver como terminar los procesos y hacerle join
            



