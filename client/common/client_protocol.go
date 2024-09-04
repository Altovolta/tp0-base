package common

import (
	"bufio"
	"fmt"
	"net"
	"strings"
)

func SendId(conn net.Conn, id string) int {
	return send_message(conn, id)
}

func AskForWinnersToServer(conn net.Conn) int {
	return send_message(conn, "3")
}

func SendBetsBatch(conn net.Conn, bets []Bet) int {

	var buf []string

	for _, bet := range bets {
		parsed_bet := bet.ParseBet()
		buf = append(buf, parsed_bet)
	}

	batch := strings.Join(buf, "")
	msg := fmt.Sprintf("%s%04d%s", "0", len(bets), batch) // le agrego el código al batch
	log.Debugf("Ya parsie, ahora envio")
	return send_message(conn, msg)
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

func ObtainWinnersAmount(reader *bufio.Reader) int {

	ganadores := 0
	for {
		msg, err := reader.ReadString('\n')
		if err != nil {
			return -1
		}
		if msg == "FIN\n" {
			break
		}
		ganadores += 1

	}
	return ganadores

}
