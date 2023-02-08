package main

import (
	"bytes"
	"crypto/ed25519"

	"github.com/algorand/go-algorand-sdk/encoding/msgpack"
	"github.com/algorand/go-algorand-sdk/types"
)

var txidPrefix = []byte("TX")

func VerifySignedTransaction(stxn types.SignedTxn) bool {
	from := stxn.Txn.Sender[:]

	encodedTx := msgpack.Encode(stxn.Txn)

	msgParts := [][]byte{txidPrefix, encodedTx}
	msg := bytes.Join(msgParts, nil)

	return ed25519.Verify(from, msg, stxn.Sig[:])
}
