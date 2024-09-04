import logging
from . import server_protocol as pr, utils
from multiprocessing import Lock, Value
BET_MESSAGE_CODE = "0"
BATCH_END_CODE = "1"
ALL_BETS_SENT_CODE = "2"
ASK_FOR_WINNERS = "3"

AMOUNT_OF_CLIENTS = 1 #5

class ClientHandler:

    def __init__(self, protocol:pr.ServerProtocol, client_id, locks, agencias_terminaron): #agregar la barrera?
        self.protocol = protocol #crear clase protocol para esto y usar las func de pr
        self.bets = []
        self.client_id = client_id
        self.locks = locks
        self.agencias_terminaron = agencias_terminaron #es tipo Value

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
                    logging.debug(f"All bets from client {self.client_id} were received")
                    self.agencias_terminaron.value += 1
                elif msg == ASK_FOR_WINNERS:
                    logging.debug(f"CLIENT WANTS WINNERS")
                    self.handle_winners_request_message()
                    break

        except ValueError as e: #agregar except para la barrera
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
        with self.locks["file"]:
            utils.store_bets(self.bets) #usar locks (ver de implementar monitor)
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(self.bets)}")
        self.bets = []
        self.protocol.send_all("OK\n")

    def handle_winners_request_message(self):
        #falta chequear de que ya se haya hecho el sorteo
        winners = self.get_winners() #esto debe llamar a un monitor? o usar locks por los menos
        logging.debug(f"THE WINNERS ARE... {winners}")
        self.protocol.send_winners(winners) #-> este metodo, pero debe ser distinto
    
    def get_winners(self):
        bets = []
        winners = []
        with self.locks["file"]:
            bets = utils.load_bets()

        for bet in bets:
            logging.debug(f"MISMO ID? {bet.agency == self.client_id}| GANO? {utils.has_won(bet)}")
            if bet.agency == self.client_id and utils.has_won(bet):
                logging.debug("I WON")
                winners.append(bet)

        return winners

        

    