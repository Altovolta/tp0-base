package common

import (
	"bufio"
	"fmt"
	"net"
	"strings"
)

// Send the id through the socket. It guarantees that there are not short writes
// It returns the numbers of bytes send and error if it fails
func SendId(conn net.Conn, id string) (int, error) {
	return send_message(conn, id)
}

// Sends a message through the socket asking for the raflle's winners
// It returns the numbers of bytes send and error if it fails
func AskForWinnersToServer(conn net.Conn, id string) (int, error) {
	msg := fmt.Sprintf("%s%s", id, ASK_FOR_WINNERS)
	return send_message(conn, msg)
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

// Gets the winners from the reader and returns the amount of winners received
// It returns the numbers of bytes send and error if it fails
func ObtainWinnersAmount(reader *bufio.Reader) (int, error) {

	ganadores := 0
	for {
		msg, err := reader.ReadString('\n')
		if err != nil {
			return 0, err
		}
		if msg == ALL_WINNERS_SENT {
			break
		}
		ganadores += 1

	}
	return ganadores, nil

}
