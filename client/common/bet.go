package common

import (
	"fmt"
	"strconv"
)

type Bet struct {
	NOMBRE     string
	APELLIDO   string
	DOCUMENTO  int
	NACIMIENTO string
	NUMERO     int
}

func NewBet(nombre string, apellido string, dni string, nacimiento string, num string) (*Bet, error) {
	documento, err := strconv.Atoi(dni)
	numero, err2 := strconv.Atoi(num)

	if err != nil || err2 != nil {

		return nil, err
	}

	bet := &Bet{
		NOMBRE:     nombre,
		APELLIDO:   apellido,
		DOCUMENTO:  documento,
		NACIMIENTO: nacimiento,
		NUMERO:     numero,
	}
	return bet, nil
}

func (bet *Bet) ParseBet() string {
	mensaje := fmt.Sprintf("%02d%-23s%02d%-10s%08d%s%04d",
		len(bet.NOMBRE), bet.NOMBRE, len(bet.APELLIDO), bet.APELLIDO,
		bet.DOCUMENTO, bet.NACIMIENTO, bet.NUMERO,
	)
	return mensaje

}
