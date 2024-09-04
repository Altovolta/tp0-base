import logging
from . import server_protocol as pr, utils
from multiprocessing import Lock, Value, Manager
from . import constants as const


class ClientHandler:

    def __init__(self, protocol:pr.ServerProtocol, client_id, lock, agencias_terminaron, winners, sorteo_realizado):
        self.protocol = protocol 
        self.bets = []
        self.client_id = client_id
        self.file_lock = lock
        self.agencias_terminaron = agencias_terminaron
        self.winners = winners
        self.sorteo_realizado = sorteo_realizado

    def run(self):

        try:

            while True: 
                msg = self.protocol.receive_message_code()
                if msg is None: #client disconnected
                    return
                
                if msg == const.BATCH_MESSAGE_CODE:
                    if self.handle_batch_message() is None:
                        break
                elif msg == const.ALL_BETS_SENT_CODE: 
                    self.handle_all_bets_sent_message()
                elif msg == const.ASK_FOR_WINNERS:
                    status = self.handle_winners_request_message()
                    if  status is None:
                        logging.error("Failed to send winners")        
                        break
                    elif status:
                        #if i already sent the winners, the connection is closed
                        break

        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(self.bets)}")
            self.protocol.send_all("E\n")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.protocol.close()


    """
    Stops the client handler execution and closes the connection socket
    """
    def stop(self):
        logging.debug(f"Closing connection for client {self.client_id}")
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
        if self.protocol.send_all("OK\n") == 0:
            return None
        return True

    """
    Handler that manages ALL_BETS_SENT command.
    If the number of agencies that sent all of its batches is the maximun amount,
    it obtains the raffle winners
    """
    def handle_all_bets_sent_message(self):
        logging.debug(f"All bets from client {self.client_id} were received")
        with self.agencias_terminaron.get_lock():
            self.agencias_terminaron.value += 1
            if self.agencias_terminaron.value < const.AMOUNT_OF_CLIENTS:
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
        client_winners = self.get_my_winners()
        if self.protocol.send_winners(client_winners) == 0:
            return None
        return True
    
    """
    Gets the winners from the storage and its saves it in self.winners array
    """
    def get_winners(self):
        bets = []
        with self.file_lock:
            bets = utils.load_bets()

        for bet in bets:
            if utils.has_won(bet):
                self.winners.append(bet)
    

    """
    Returns the winner bets that has the id of the client
    """
    def get_my_winners(self):
        my_winners = []

        for winner in self.winners:
            if winner.agency == self.client_id:
                my_winners.append(winner)
        return my_winners
       

    