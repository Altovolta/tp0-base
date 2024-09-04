package common

// Protocol
const BATCH_MESSAGE_CODE = "0"
const ALL_BETS_SENT_CODE = "2"
const ASK_FOR_WINNERS = "3"

// Command code from server
const BATCH_RECEIVED_SUCCESS = "OK\n"
const BATCH_RECEIVED_FAILED = "E\n"
const RAFFLE_PENDING = "N\n"
const RAFFLE_READY = "Y\n"
const ALL_WINNERS_SENT = "FIN\n"
