package main

import (
	"context"
	"log"

	"github.com/algorand/go-algorand-sdk/client/v2/algod"
)

var (
	algodAddress = "https://testnet-api.algonode.cloud"
	algodToken   = ""
)

func main() {
	client, err := algod.MakeClient(algodAddress, algodToken)
	if err != nil {
		log.Fatalf("Failed to make client: %+v", err)
	}

	start := 22056376
	for i := 0; i < 1000; i++ {
		block, err := client.Block(uint64(i + start)).Do(context.Background())
		if err != nil {
			log.Printf("Failed to get block: %+v")
		}
		txns := len(block.Payset)
		if txns == 0 {
			return
		}
	}

}
