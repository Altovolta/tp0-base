import socket
import logging

import signal

from common.client_handler import *
from common.server_protocol import *
from common.constants import *
from multiprocessing import Process, Lock, Value, Manager

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.agencias_terminaron = Value('i', 0) #shared value
        self.file_lock = Lock()  #shared lock for storing bets
        self.manager = Manager()
        self.winners = self.manager.dict() #shared dict
        self.sorteo_realizado =  Value('i', 0) #shared value used as a bool
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
                break
            self.__handle_client_connection(client_sock)

        #stop and join processes before closing the server
        if not self._got_close_signal:
            logging.info("Server socket closed")
            self._server_socket.close()
            logging.info("Closing handlers sockets")
            for client in self.clients:
                client.stop()
            logging.info("Joining process handles")
            for handle in self._clients_handles:
                handle.join()
            
  
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        protocol = ServerProtocol(client_sock)
        cli_id = protocol.recv_bytes(1) #recieves the client id
        if cli_id is None:
            protocol.close()
            return
        client_handler = ClientHandler(protocol, cli_id, self.file_lock, self.agencias_terminaron, self.winners, self.sorteo_realizado)
        self.clients.append(client_handler) #save the client for closing sockets
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
        
    def sigterm_handler(self, signal, frame):
        logging.info("Server socket closed")
        self._got_close_signal = True
        self._server_socket.close()
        logging.info("Closing handlers sockets")
        for client in self.clients:
            client.stop()
        logging.info("Joining process handles")
        for handle in self._clients_handles:
            handle.join()
            



