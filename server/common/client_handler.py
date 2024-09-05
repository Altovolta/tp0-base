import logging
from . import utils
from common.constants import *
from common.server_protocol import *
from multiprocessing import Queue

class ClientHandler:

    def __init__(self, protocol:ServerProtocol, client_id, lock, queue_to_server:Queue, queue_from_server:Queue):
        self.protocol = protocol 
        self.bets = []
        self.client_id = client_id
        self.file_lock = lock #shared lock
        self.queue_to_server = queue_to_server
        self.queue_from_server = queue_from_server

    def run(self):

        try:

            while True: 
                msg = self.protocol.receive_message_code()
                if msg is None: #client disconnected
                    return
                
                if msg == BATCH_MESSAGE_CODE:
                    if self.handle_batch_message() is None:
                        break
                elif msg == ALL_BETS_SENT_CODE: 
                    self.handle_all_bets_sent_message()
                elif msg == ASK_FOR_WINNERS:
                    status = self.handle_winners_request_message()
                    if  status is None:
                        logging.error("Failed to send winners")        
                        break
                    elif status:
                        #if i already sent the winners, the connection is closed
                        break

        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(self.bets)}")
            self.protocol.send_all(BATCH_RECEIVED_FAILED)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.protocol.close()


    """
    Stops the client handler execution and closes the connection socket
    """
    def stop(self):
        logging.info(f"Closing connection for client {self.client_id}")
        self.protocol.close()
        self.queue_to_server.put((self.client_id, PROTOCOL_CLOSED))

    """
    Handler that receives the batch of bets and stores them
    """

    def handle_batch_message(self):
        bets = self.protocol.receive_batch(self.client_id)
        if bets is None:
            return
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
        with self.file_lock:
            utils.store_bets(bets)
        if self.protocol.send_all(BATCH_RECEIVED_SUCCESS) == 0:
            return None
        return True

    """
    Handler that manages ALL_BETS_SENT command.
    If the number of agencies that sent all of its batches is the maximun amount,
    it obtains the raffle winners
    """
    def handle_all_bets_sent_message(self):
        logging.info(f"All bets from client {self.client_id} were received")
        self.queue_to_server.put((self.client_id, CLIENT_FINISHED))

    """
    Handles the ASK_FOR_WINNERS command. If the draw was made, it send the 
    winners of an agency to the client
    """
    def handle_winners_request_message(self):

        self.queue_to_server.put((self.client_id, CONSULT_WINNERS))

        winners = self.queue_from_server.get()
        if winners is None:
            self.protocol.send_raffle_pending()
            return False #no se hizo el sorteo
        
        if self.protocol.send_winners(winners) == 0:
            return None
        return True
    