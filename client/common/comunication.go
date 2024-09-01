package common

import "fmt"

func SendBetsBatch(c *Client, bets []Bet) int {

	for _, bet := range bets {
		res := SendBet(c, &bet)

		if res == -1 {
			return -1
		}
	}
	return SendBatchEnd(c)
}

func SendBet(c *Client, bet *Bet) int {
	bet_msg_code := "0"
	bet_string := bet.ParseBet()
	mensaje := fmt.Sprintf("%s%s", bet_msg_code, bet_string)
	return send_message(c, mensaje)
}

func SendBatchEnd(c *Client) int {
	batch_end_code := "1"
	return send_message(c, batch_end_code)
}

func SendAllBetsSent(c *Client) int {
	all_bets_sent_code := "2"
	return send_message(c, all_bets_sent_code)
}

func send_message(c *Client, msg string) int {
	bytes_to_send := len(msg)
	bytes_sent := 0

	for bytes_to_send > bytes_sent {

		n, err := c.conn.Write([]byte(msg[bytes_sent:]))
		if err != nil {
			// the socket was closed
			return -1
		}
		bytes_sent += n
	}
	return 0
}
