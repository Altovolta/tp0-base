package common

import (
	"fmt"
	"net"
)

func SendId(conn net.Conn, id string) int {
	return send_message(conn, id)
}

func SendBetsBatch(conn net.Conn, bets []Bet) int {

	for _, bet := range bets {
		res := SendBet(conn, &bet)

		if res == -1 {
			return -1
		}
	}
	return SendBatchEnd(conn)
}

func SendBet(conn net.Conn, bet *Bet) int {
	bet_msg_code := "0"
	bet_string := bet.ParseBet()
	mensaje := fmt.Sprintf("%s%s", bet_msg_code, bet_string)
	return send_message(conn, mensaje)
}

func SendBatchEnd(conn net.Conn) int {
	batch_end_code := "1"
	return send_message(conn, batch_end_code)
}

func SendAllBetsSent(conn net.Conn) int {
	all_bets_sent_code := "2"
	return send_message(conn, all_bets_sent_code)
}

func send_message(conn net.Conn, msg string) int {
	bytes_to_send := len(msg)
	bytes_sent := 0

	for bytes_to_send > bytes_sent {

		n, err := conn.Write([]byte(msg[bytes_sent:]))
		if err != nil {
			// the socket was closed
			return -1
		}
		bytes_sent += n
	}
	return 0
}
