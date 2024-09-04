import logging
from . import server_protocol as pr, utils
from multiprocessing import Lock, Value, Manager
BET_MESSAGE_CODE = "0"
BATCH_END_CODE = "1"
ALL_BETS_SENT_CODE = "2"
ASK_FOR_WINNERS = "3"

AMOUNT_OF_CLIENTS = 5

class ClientHandler:

    def __init__(self, protocol:pr.ServerProtocol, client_id, lock, agencias_terminaron, winners, sorteo_realizado):
        self.protocol = protocol #crear clase protocol para esto y usar las func de pr
        self.bets = []
        self.client_id = client_id
        self.file_lock = lock
        self.agencias_terminaron = agencias_terminaron #es tipo Value
        self.winners = winners
        self.sorteo_realizado = sorteo_realizado

    def run(self):

        try:

            while True: 
                msg = self.protocol.recv_bytes(1)
                if msg is None: #se desconecto el cliente
                    return
                
                if msg == BET_MESSAGE_CODE:
                    self.handle_bet_message()
                elif msg == BATCH_END_CODE:
                    self.handle_batch_end_message()
                elif msg == ALL_BETS_SENT_CODE: 
                    self.handle_all_bets_sent_message()
                elif msg == ASK_FOR_WINNERS:
                    if self.handle_winners_request_message():
                        # ya envié los ganadores, entonces cierro la conexión
                        break

        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(self.bets)}")
            self.protocol.send_all("E\n")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.protocol.close()

    def stop(self):
        self.protocol.close()

    def handle_bet_message(self):
        bet = self.protocol.receive_bet_message(self.client_id)
        self.bets.append(bet)

    def handle_batch_end_message(self):
        with self.file_lock:
            utils.store_bets(self.bets)
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(self.bets)}")
        self.bets = []
        self.protocol.send_all("OK\n")

    def handle_all_bets_sent_message(self):
        logging.debug(f"All bets from client {self.client_id} were received")
        with self.agencias_terminaron.get_lock():
            self.agencias_terminaron.value += 1
            if self.agencias_terminaron.value < AMOUNT_OF_CLIENTS:
                return
        # Si es el último en terminar de enviar las apuestas, realiza el sorteo
        self.get_winners()
        #indico que se realizo el sorteo
        with self.sorteo_realizado.get_lock():
            self.sorteo_realizado.value = True
        
        logging.info("action: sorteo | result: success")

    def handle_winners_request_message(self): #devuelvo true o false para saber si ya lo envié y si salgo?
        with self.sorteo_realizado.get_lock():
            if self.sorteo_realizado.value == False:
                self.protocol.send_raffle_pending()
                return False
        client_winners = self.get_my_winners()
        self.protocol.send_winners(client_winners)
        return True
    
    def get_winners(self):
        bets = []
        with self.file_lock:
            bets = utils.load_bets()

        for bet in bets:
            if utils.has_won(bet):
                self.winners.append(bet)
    
    def get_my_winners(self):
        my_winners = []

        for winner in self.winners:
            if winner.agency == self.client_id:
                my_winners.append(winner)
        return my_winners
       

    