import logging
from . import utils
from common.constants import *
from common.server_protocol import *


class ClientHandler:

    def __init__(self, protocol:ServerProtocol, client_id, lock, agencias_terminaron, winners, sorteo_realizado):
        self.protocol = protocol 
        self.bets = []
        self.client_id = client_id
        self.file_lock = lock #shared lock
        self.agencias_terminaron = agencias_terminaron #shared value
        self.winners = winners #shared dict
        self.sorteo_realizado = sorteo_realizado #shared value

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
        with self.agencias_terminaron.get_lock():
            self.agencias_terminaron.value += 1
            if self.agencias_terminaron.value < AMOUNT_OF_CLIENTS:
                return
        # if its the last one to send all the bets, it loads the winners
        self.get_winners()
        with self.sorteo_realizado.get_lock():
            self.sorteo_realizado.value = True
        
        logging.info("action: sorteo | result: success")


    """
    Handles the ASK_FOR_WINNERS command. If the draw was made, it send the 
    winners of an agency to the client
    """
    def handle_winners_request_message(self):
        with self.sorteo_realizado.get_lock():
            if self.sorteo_realizado.value == False:
                self.protocol.send_raffle_pending()
                return False

        client_winners = self.winners.get(self.client_id, [])
        if self.protocol.send_winners(client_winners) == 0:
            return None
        return True
    
    """
    Gets the winners from the storage and its saves it in self.winners array
    """
    def get_winners(self):
        bets_per_client = {}
        with self.file_lock:
           bets_per_client = utils.get_winners()

        # Because of how the Manager dict works, i need to assign
        # the different lists that are in bets_per_clients dictionary
        # for them to be shared. Appending to the list inside the shared 
        # dict does not update the shared dictionary
        for cli_id, bets in bets_per_client.items():
                self.winners[cli_id] = bets
    