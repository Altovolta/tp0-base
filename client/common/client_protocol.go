package common

import "net"

// Sends a bet trough the socket. It guarantees that there are not short writes
// It returns the numbers of bytes send and error if it fails
func SendBet(conn net.Conn, bet *Bet) (int, error) {

	mensaje := bet.ParseBet()
	bytes_to_send := len(mensaje)
	bytes_sent := 0

	for bytes_to_send > bytes_sent {

		n, err := conn.Write([]byte(mensaje[bytes_sent:]))
		if err != nil {
			return 0, err
		}
		bytes_sent += n
	}
	return bytes_sent, nil
}
