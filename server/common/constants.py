#defines the max number of agencies the server supports
AMOUNT_OF_CLIENTS = 5

#Command codes from client
BATCH_MESSAGE_CODE = "0"
ALL_BETS_SENT_CODE = "2"
ASK_FOR_WINNERS = "3"

#Command code from server to client
RAFFLE_PENDING = "N\n"
RAFFLE_READY = "Y\n"
ALL_WINNERS_SENT = "FIN\n"
BATCH_RECEIVED_SUCCESS = "OK\n"
BATCH_RECEIVED_FAILED = "E\n"

#bytes amount
BET_LEN = 59
AMOUNT_OF_BETS_IN_BATCH_LEN = 4

#Server and Handlers comunication

WAITING_FOR_OTHER_CLIENTS = None
CLIENT_FINISHED = "OK"
CONSULT_WINNERS = "P"
PROTOCOL_CLOSED = "C"

