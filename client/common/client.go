package common

import (
	"bufio"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	BatchSize     int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	stop   bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		stop:   false,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	sig_channel := make(chan os.Signal, 1)
	signal.Notify(sig_channel, syscall.SIGTERM)

	file, erro := os.Open("agency.csv")
	if erro != nil {
		log.Criticalf("hubo un error: %s", erro)
		return
	}
	defer file.Close()

	c.createClientSocket()

	go func() {
		sig := <-sig_channel
		log.Info("signal received | signal: %s", sig)
		c.stop = true
		c.conn.Close()
		log.Infof("Closing file and socket connection")
	}()

	_, err := SendId(c.conn, c.config.ID)
	if err != nil {
		process_error(err, c.stop, c.config.ID)
		c.conn.Close()
		log.Infof("Closing socket connection")
		return
	}

	fscanner := bufio.NewScanner(file)
	reader := bufio.NewReader(c.conn)

	for {

		bets, err := get_bet_batch(fscanner, c.config.BatchSize)
		if err != nil {
			log.Criticalf("Couldn get batch. Error:  %v", err)
			c.conn.Close()
			log.Infof("Closing socket connection")
			return
		}
		_, err = SendBetsBatch(c.conn, bets)
		if err != nil {
			process_error(err, c.stop, c.config.ID)
			c.conn.Close()
			log.Infof("Closing socket connection")
			return
		}

		msg, err := reader.ReadString('\n')
		if err != nil {
			process_error(err, c.stop, c.config.ID)
			c.conn.Close()
			log.Infof("Closing socket connection")
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			c.config.ID,
			msg,
		)
		if msg != BATCH_RECEIVED_SUCCESS {
			log.Errorf("action: send_batch | result: fail | client_id: %v", c.config.ID)
			c.conn.Close()
			log.Infof("Closing socket connection")
			return
		}

		if len(bets) < c.config.BatchSize {
			_, err := SendAllBetsSent(c.conn)
			if err != nil {
				process_error(err, c.stop, c.config.ID)
				c.conn.Close()
				log.Infof("Closing socket connection")
				return
			}
			break
		}

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Debugf("action: loop_finished | result: success | client_id: %v", c.config.ID)
	c.conn.Close()

	c.GetWinners()
}

// Ask for the winners to the server.
func (c *Client) GetWinners() {

	for !c.stop {
		c.createClientSocket()
		reader := bufio.NewReader(c.conn)
		AskForWinnersToServer(c.conn, c.config.ID)

		msg, err := reader.ReadString('\n')
		if err != nil {
			process_error(err, c.stop, c.config.ID)
			c.conn.Close()
			log.Infof("Closing socket connection")
			return
		}
		switch msg {
		case RAFFLE_PENDING:
			log.Infof("Raffle not ready")
			time.Sleep(c.config.LoopPeriod)
			c.conn.Close()
		case RAFFLE_READY:
			cant_ganadores, err := ObtainWinnersAmount(reader)
			if err != nil {
				log.Errorf("Error while receiving winners")
				c.conn.Close()
				log.Infof("Closing socket connection")
				return
			}

			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", cant_ganadores)
			c.conn.Close()
			log.Infof("Closing socket connection")
			return
		}

	}
}
