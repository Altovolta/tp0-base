package common

import (
	"fmt"
	"os"
	"strconv"
)

type Bet struct {
	NOMBRE     string
	APELLIDO   string
	DOCUMENTO  int
	NACIMIENTO string
	NUMERO     int
}

func NewBet() *Bet {
	documento, _ := strconv.Atoi(os.Getenv("DOCUMENTO"))
	numero, _ := strconv.Atoi(os.Getenv("NUMERO"))

	bet := &Bet{
		NOMBRE:     os.Getenv("NOMBRE"),
		APELLIDO:   os.Getenv("APELLIDO"),
		DOCUMENTO:  documento,
		NACIMIENTO: os.Getenv("NACIMIENTO"),
		NUMERO:     numero,
	}
	return bet
}

func (bet *Bet) ParseBet() string {
	client_id := os.Getenv("CLI_ID")
	mensaje := fmt.Sprintf("%s%02d%-23s%02d%-10s%08d%s%02d",
		client_id, len(bet.NOMBRE), bet.NOMBRE, len(bet.APELLIDO), bet.APELLIDO,
		bet.DOCUMENTO, bet.NACIMIENTO, bet.NUMERO,
	)
	return mensaje

}

func SendBet(c *Client, bet *Bet) int {

	mensaje := bet.ParseBet()
	bytes_to_send := len(mensaje)
	bytes_sent := 0

	for bytes_to_send > bytes_sent {

		n, err := c.conn.Write([]byte(mensaje[bytes_sent:]))
		//ver de usar Write de enconding/binary -> asi lo paso a BigEndian
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
