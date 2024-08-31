package common

func SendBet(c *Client, bet *Bet) int {

	mensaje := bet.ParseBet()
	bytes_to_send := len(mensaje)
	bytes_sent := 0

	for bytes_to_send > bytes_sent {

		n, err := c.conn.Write([]byte(mensaje[bytes_sent:]))
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return -1
		}
		bytes_sent += n
	}
	return 0
}
