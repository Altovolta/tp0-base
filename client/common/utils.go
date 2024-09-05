package common

import (
	"bufio"
	"strings"
)

// Get batch size bets from a file. If there is an error, err is set.
// It returns an array of bets.
func get_bet_batch(fscanner *bufio.Scanner, batch_size int) ([]Bet, error) {
	var bets []Bet
	bets_loaded := 0
	for fscanner.Scan() {

		line := fscanner.Text()
		bet_params := strings.Split(line, ",")

		bet, err := NewBet(bet_params[0], bet_params[1], bet_params[2], bet_params[3], bet_params[4])
		if err != nil {
			return nil, err
		}
		bets = append(bets, *bet)

		bets_loaded += 1
		if bets_loaded >= batch_size {
			break
		}
	}

	return bets, nil
}

// Handle errors when receiving messages from socket
func process_error(err error, stop_signal bool, client_id string) {

	if stop_signal {
		return
	}
	log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
		client_id,
		err,
	)
}
