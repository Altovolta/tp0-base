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

// func SendBetsBatch(c *Client, bets []Bet) int {

// 	for _, bet := range bets {
// 		res := SendBet(c, &bet)

// 		if res == -1 {
// 			return -1
// 		}
// 	}
// 	return SendBatchEnd(c)
// }

// func SendBet(c *Client, bet *Bet) int {
// 	bet_msg_code := "0"
// 	bet_string := bet.ParseBet()
// 	mensaje := fmt.Sprintf("%s%s", bet_msg_code, bet_string)
// 	return send_message(c, mensaje)
// }

// func SendBatchEnd(c *Client) int {
// 	batch_end_code := "1"
// 	return send_message(c, batch_end_code)
// }

// func SendAllBetsSent(c *Client) int {
// 	all_bets_sent_code := "2"
// 	return send_message(c, all_bets_sent_code)
// }

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

// func send_message(c *Client, msg string) int {
// 	bytes_to_send := len(msg)
// 	bytes_sent := 0

// 	for bytes_to_send > bytes_sent {

// 		n, err := c.conn.Write([]byte(msg[bytes_sent:]))
// 		if err != nil {
// 			// the socket was closed
// 			return -1
// 		}
// 		bytes_sent += n
// 	}
// 	return 0
// }
