package common

import (
	"fmt"
	"net"
	"strings"
)

// Send the id through the socket. It guarantees that there are not short writes
// It returns the numbers of bytes send and error if it fails
func SendId(conn net.Conn, id string) (int, error) {
	return send_message(conn, id)
}

// Receives an array of Bets and sends them in one batch through the socket
// It returns the numbers of bytes send and error if it fails
func SendBetsBatch(conn net.Conn, bets []Bet) (int, error) {

	var buf []string

	for _, bet := range bets {
		parsed_bet := bet.ParseBet()
		buf = append(buf, parsed_bet)
	}

	batch := strings.Join(buf, "")
	msg := fmt.Sprintf("%s%04d%s", BATCH_MESSAGE_CODE, len(bets), batch)
	return send_message(conn, msg)

}

// Send through the socket that there are no more bets to send
// It returns the numbers of bytes send and error if it fails
func SendAllBetsSent(conn net.Conn) (int, error) {
	return send_message(conn, ALL_BETS_SENT_CODE)
}

// Sends a message through the socket. It guarantees that there are not short writes
// It returns the numbers of bytes send and error if it fails
func send_message(conn net.Conn, msg string) (int, error) {
	bytes_to_send := len(msg)
	bytes_sent := 0

	for bytes_to_send > bytes_sent {

		n, err := conn.Write([]byte(msg[bytes_sent:]))
		if err != nil {
			// the socket was closed
			return -1, err
		}
		bytes_sent += n
	}
	return 0, nil
}
