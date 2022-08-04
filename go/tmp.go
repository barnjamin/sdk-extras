package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

	"github.com/algorand/go-algorand/data/bookkeeping"
	"github.com/algorand/go-algorand/protocol"
	"github.com/algorand/go-algorand/rpcs"
)

func get(algodUrl string, algodToken string, path string) (body []byte, err error) {
	client := http.Client{}
	req, err := http.NewRequest("GET", algodUrl+path, nil)
	if err != nil {
		return
	}

	req.Header = http.Header{
		"Content-Type":     {"application/json"},
		"X-Algo-API-Token": {algodToken},
	}

	resp, err := client.Do(req)
	if err != nil {
		return
	}

	defer resp.Body.Close()

	body, err = ioutil.ReadAll(resp.Body)
	return
}

func getLastRound(algodUrl string, algodToken string) (lastRound uint64, err error) {

	body, err := get(algodUrl, algodToken, "/v2/status")
	if err != nil {
		return
	}
	var data map[string]interface{}

	err = json.Unmarshal(body, &data)
	if err != nil {
		return
	}

	lastRound = uint64(data["last-round"].(float64))
	return
}

func getBlock(algodUrl string, algodToken string, round uint64) (bookkeeping.Block, error) {
	block := rpcs.EncodedBlockCert{}
	body, err := get(algodUrl, algodToken, fmt.Sprintf("/v2/blocks/%d?format=msgpack", round))
	if err != nil {
		return block.Block, err
	}

	err = protocol.Decode(body, &block)
	if err != nil {
		return block.Block, err
	}
	return block.Block, err
}

func main() {
	algodUrl := "http://localhost:4001"
	algodToken := strings.Repeat("a", 64)

	lastRound, err := getLastRound(algodUrl, algodToken)
	if err != nil {
		log.Fatal(err)
	}

	round := lastRound
	fmt.Print("\n")
	response, err := getBlock(algodUrl, algodToken, round)
	if err != nil {
		log.Fatal(err)
	}

	// Here we would like to just use the existing deserialisers to get back the full data
	// structure, which should be something like
	//
	// type blockRawResponse struct {
	//     Block       bookkeeping.Block     `codec:"block"`
	//     Certificate agreement.Certificate `codec:"cert"`
	// }

	log.Printf("%+v", response)

}
