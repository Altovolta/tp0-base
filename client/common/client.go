package common

import (
	"bufio"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	//"encoding/binary"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
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
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed

	sig_channel := make(chan os.Signal, 1)
	signal.Notify(sig_channel, syscall.SIGTERM)

	select {
	case sig := <-sig_channel:
		log.Debugf("signal received | signal: %s", sig)
		return
	default:
	}

	c.createClientSocket()

	bet := NewBet()
	status := SendBet(c, bet)

	if status != 0 {
		log.Errorf("Fallo al enviar mensaje", c.config.ID)
		c.conn.Close()
		return
	}
	_, err := bufio.NewReader(c.conn).ReadString('\n')

	c.conn.Close()

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	log.Infof("action: apuesta_enviada | result: success | dni: %d | numero: %d", bet.DOCUMENTO, bet.NUMERO)

	// Wait a time between sending one message and the next one
	time.Sleep(c.config.LoopPeriod)

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
