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
		log.Debugf("signal received | signal: %s", sig)
		c.stop = true
		c.conn.Close()
		log.Debugf("Closing file and socket connection")
	}()

	status := SendId(c.conn, c.config.ID)
	if status == -1 {
		//socket was closed
		return
	}

	fscanner := bufio.NewScanner(file)
	reader := bufio.NewReader(c.conn)

	for {

		bets := get_bet_batch(fscanner, c.config.BatchSize)
		status := SendBetsBatch(c.conn, bets)
		if status == -1 {
			//if the socket was closed, return
			return
		}

		msg, err := reader.ReadString('\n')
		if err != nil {
			if c.stop {
				return
			}
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			c.config.ID,
			msg,
		)
		if msg != "OK\n" {
			log.Errorf("action: send_batch | result: fail | client_id: %v", c.config.ID)
		}

		if len(bets) < c.config.BatchSize {
			result := SendAllBetsSent(c.conn)
			if result == -1 {
				return
			}
			break
		}

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
	//c.conn.Close()

	c.GetWinners()
}

func (c *Client) GetWinners() {

	for !c.stop {
		//c.createClientSocket()
		reader := bufio.NewReader(c.conn)
		AskForWinnersToServer(c.conn, c.config.ID)

		msg, err := reader.ReadString('\n')
		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			break
		}
		switch msg {
		case "N\n":
			log.Debugf("Todavía no se realizó el sorteo")
			time.Sleep(c.config.LoopPeriod)
		case "Y\n":
			cant_ganadores := ObtainWinnersAmount(reader)
			if cant_ganadores == -1 {
				log.Errorf("Error while receiving winners")
			}
			log.Debugf("action: consulta_ganadores | result: success | cant_ganadores: %v", cant_ganadores)
			c.conn.Close()
			return
		}

	}
}
