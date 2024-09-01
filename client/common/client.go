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
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
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
	defer file.Close() // close the file when func end
	c.createClientSocket()

	fscanner := bufio.NewScanner(file)

	go func() {
		sig := <-sig_channel
		log.Debugf("signal received | signal: %s", sig)
		file.Close()
		c.conn.Close()
		log.Debugf("Closing file and socket connection")
	}()

	for {

		bets := get_bet_batch(fscanner, c.config.BatchSize)
		status := SendBetsBatch(c, bets)
		//if the socket was closed, return
		if status == -1 {
			return
		}

		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			break
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			c.config.ID,
			msg,
		)
		if msg != "OK\n" {
			log.Errorf("action: send_batch | result: fail | client_id: %v", c.config.ID)
		}

		if len(bets) < c.config.BatchSize {
			SendAllBetsSent(c)
			break
		}

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
	file.Close()
	c.conn.Close()
}
