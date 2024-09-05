import socket
import logging

import signal

from common.client_handler import *
from common.server_protocol import *
from common.constants import *
from multiprocessing import Process, Lock, Queue

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self.agencias_terminaron = 0 
        self.file_lock = Lock()  #shared lock for storing bets
        self.winners = {}
        self.clients_queues: dict[str, Queue] = {}
        self.client_to_server_queue = Queue()
        self._got_close_signal = False
        self._clients_process_handles = []
        self.clients = []
        self.clients_accepted = 0

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

            if self.clients_accepted == AMOUNT_OF_CLIENTS:
                if self.handle_queues():
                    self.send_winners()
                    break

        self.close_server()
            
  
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
        client_queue = Queue()
        self.clients_queues[cli_id] = client_queue

        client_handler = ClientHandler(protocol, cli_id, self.file_lock, self.client_to_server_queue, client_queue)
        self.clients.append(client_handler) #save the client for closing sockets

        p = Process(target=client_handler.run, args=())
        p.start()
        
        self._clients_process_handles.append(p)
        self.clients_accepted += 1

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
    
    """
    Gets the winners and sends it to the clients handlers
    """
    def send_winners(self):
        self.winners = utils.get_winners()
        logging.info("action: sorteo | result: success")

        for client, queue in self.clients_queues.items():
            winners = self.winners.get(client, [])
            queue.put(winners)

    """
    Server starts to handle the comunication with the client handlers.
    It returns true if all the clients sent all their bets
    """
    def handle_queues(self):

        while self.agencias_terminaron != 5:
            if self._got_close_signal:
                return False

            cli_id, msg = self.client_to_server_queue.get()
            if msg == CLIENT_FINISHED:
                self.agencias_terminaron += 1
            elif msg == PROTOCOL_CLOSED:
                return False
            if self.agencias_terminaron == AMOUNT_OF_CLIENTS:
                return True
            else:
                self.clients_queues[cli_id].put(WAITING_FOR_OTHER_CLIENTS)

    """
    Closes the server open resources
    """
    def close_server(self):

        logging.info("Waiting for clients to finish")
        for handle in self._clients_process_handles:
            handle.join()
        logging.info("Process handles joined")
        if not self._got_close_signal:
            logging.info("Server socket closed")
            self._server_socket.close()
            logging.info("Closing handlers sockets")
            for client in self.clients:
                client.stop()

