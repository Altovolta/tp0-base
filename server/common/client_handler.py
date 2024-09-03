import logging
from . import server_protocol as pr, utils

BET_MESSAGE_CODE = "0"
BATCH_END_CODE = "1"
ALL_BETS_SENT_CODE = "2"
ASK_FOR_WINNERS = "3"

class ClientHandler:

    def __init__(self, protocol:pr.ServerProtocol, client_id): #agregar la barrera?
        self.protocol = protocol #crear clase protocol para esto y usar las func de pr
        self.bets = []
        self.client_id = client_id

    def run(self):

        try:
            client_id = self.protocol.receive_message_code()#recibir esto apenas creo el handler para pasarlo por parametro
            logging.debug(f"CLIENT {client_id} connected")

            while True: 
                msg = self.protocol.recv_bytes(self.client_sock, 1)
                if msg is None: #se desconecto el cliente
                    return
                
                if msg == BET_MESSAGE_CODE:
                    self.handle_bet_message()
                elif msg == BATCH_END_CODE:
                    self.handle_batch_end_message()
                elif msg == ALL_BETS_SENT_CODE: #aca debería bloquearme en una barrera? -> hacer break
                    logging.debug(f"All bets from client {client_id} were received")
                    break
                elif msg == ASK_FOR_WINNERS:
                    self.handle_winners_request_message()

        except ValueError as e: #agregar except para la barrera
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(self.bets)}")
            pr.send_all(self.client_sock, "E\n")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.protocol.close()

    def close(self):
        self.protocol.close()

    def handle_bet_message(self):
        bet = self.protocol.receive_bet_message(self.client_id, self.client_sock)
        self.bets.append(bet)

    def handle_batch_end_message(self):
        utils.store_bets(self.bets) #usar monitor (asi hago los locks)
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(self.bets)}")
        self.bets = []
        self.protocol.send_all("OK\n")

    def handle_winners_request_message(self):
        winners = self.get_winners() #esto debe llamar a un monitor? o usar locks por los menos
        #pr.send_winners(self.client_sock, self.client_id) -> este metodo, pero debe ser distinto

    