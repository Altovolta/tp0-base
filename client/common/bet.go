package common

import (
	"bufio"
	"fmt"
	"strconv"
	"strings"
)

type Bet struct {
	NOMBRE     string
	APELLIDO   string
	DOCUMENTO  int
	NACIMIENTO string
	NUMERO     int
}

func NewBet(nombre string, apellido string, dni string, nacimiento string, num string) *Bet {
	documento, _ := strconv.Atoi(dni)
	numero, _ := strconv.Atoi(num)

	bet := &Bet{
		NOMBRE:     nombre,
		APELLIDO:   apellido,
		DOCUMENTO:  documento,
		NACIMIENTO: nacimiento,
		NUMERO:     numero,
	}
	return bet
}

func (bet *Bet) ParseBet() string {
	mensaje := fmt.Sprintf("%02d%-23s%02d%-10s%08d%s%04d",
		len(bet.NOMBRE), bet.NOMBRE, len(bet.APELLIDO), bet.APELLIDO,
		bet.DOCUMENTO, bet.NACIMIENTO, bet.NUMERO,
	)
	return mensaje

}

func get_bet_batch(fscanner *bufio.Scanner, batch_size int) []Bet {
	var bets []Bet
	bets_loaded := 0
	for fscanner.Scan() {

		line := fscanner.Text()
		bet_params := strings.Split(line, ",")

		bet := NewBet(bet_params[0], bet_params[1], bet_params[2], bet_params[3], bet_params[4])
		bets = append(bets, *bet)

		bets_loaded += 1
		if bets_loaded >= batch_size {
			break
		}
	}

	return bets
}
