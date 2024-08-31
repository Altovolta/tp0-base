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
	mensaje := fmt.Sprintf("%02d%-23s%02d%-10s%08d%s%02d",
		len(bet.NOMBRE), bet.NOMBRE, len(bet.APELLIDO), bet.APELLIDO,
		bet.DOCUMENTO, bet.NACIMIENTO, bet.NUMERO,
	)
	return mensaje

}

func (c *Client) SendBet(bet *Bet) int {

	mensaje := bet.ParseBet()
	bytes_to_send := len(mensaje) + 1

	for bytes_to_send != 0 {

		n, err := fmt.Fprintf(c.conn, "%s%s", c.config.ID, mensaje)
		//ver de usar Write de enconding/binary -> asi lo paso a BigEndian
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return -1
		}

		bytes_to_send -= n
		mensaje = mensaje[n-1:]
	}
	return 0
}
