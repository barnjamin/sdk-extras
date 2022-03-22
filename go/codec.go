package main

import (
	"context"
	"encoding/base64"
	"log"
	"os"
	"strings"

	"github.com/algorand/go-algorand-sdk/client/v2/algod"
	"github.com/algorand/go-algorand-sdk/crypto"
	"github.com/algorand/go-algorand-sdk/encoding/msgpack"
	"github.com/algorand/go-algorand-sdk/future"
	"github.com/algorand/go-algorand-sdk/types"
)

func main() {
	client, err := algod.MakeClient("http://127.0.0.1:4001", strings.Repeat("a", 64))
	if err != nil {
		log.Fatalf("Failed to init client: %+v", err)
	}

	accts, err := GetAccounts()
	if err != nil {
		log.Fatalf("Failed to get accounts: %+v", err)
	}

	acct1 := accts[1]
	acct2 := accts[2]

	// Error handling omitted for brevity
	sp, _ := client.SuggestedParams().Do(context.Background())

	pay_txn, _ := future.MakePaymentTxn(acct1.Address.String(), acct2.Address.String(), 10000, nil, "", sp)

	var pay_txn_bytes = make([]byte, 1e3)
	base64.StdEncoding.Encode(pay_txn_bytes, msgpack.Encode(pay_txn))
	f, _ := os.Create("pay.txn")
	f.Write(pay_txn_bytes)

	_, spay_txn, _ := crypto.SignTransaction(acct1.PrivateKey, pay_txn)

	var spay_txn_bytes = make([]byte, 1e3)
	base64.StdEncoding.Encode(spay_txn_bytes, spay_txn)
	f2, _ := os.Create("signed_pay.txn")
	f2.Write(spay_txn_bytes)

	var (
		recovered_pay_txn   = types.Transaction{}
		recovered_pay_bytes = make([]byte, 1e3)
	)
	b64_pay_bytes, _ := os.ReadFile("pay.txn")
	base64.StdEncoding.Decode(recovered_pay_bytes, b64_pay_bytes)

	msgpack.Decode(recovered_pay_bytes, &recovered_pay_txn)
	log.Printf("%+v", recovered_pay_txn)

	var (
		recovered_signed_pay_txn   = types.SignedTxn{}
		recovered_signed_pay_bytes = make([]byte, 1e3)
	)
	b64_signed_pay_bytes, _ := os.ReadFile("signed_pay.txn")
	base64.StdEncoding.Decode(recovered_signed_pay_bytes, b64_signed_pay_bytes)

	msgpack.Decode(recovered_signed_pay_bytes, &recovered_signed_pay_txn)
	log.Printf("%+v", recovered_signed_pay_txn)

}
