package common

// Protocol
const BATCH_MESSAGE_CODE = "0"
const ALL_BETS_SENT_CODE = "2"

// Command code from server
const BATCH_RECEIVED_SUCCESS = "OK\n"
const BATCH_RECEIVED_FAILED = "E\n"

// Restrictions
const MAX_BATCH_BYTE_SIZE = 8000
const BET_BYTE_SIZE = 59
const BATCH_HEADER_SIZE = 5 //tipo de mensaje + cantidad de apuestas en el batch
