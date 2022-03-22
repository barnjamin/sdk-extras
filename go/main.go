package main

//import (
//	"context"
//	"encoding/base64"
//	"log"
//	"os"
//	"strings"
//
//	"github.com/algorand/go-algorand-sdk/client/v2/algod"
//	"github.com/algorand/go-algorand-sdk/crypto"
//	"github.com/algorand/go-algorand-sdk/encoding/msgpack"
//	"github.com/algorand/go-algorand-sdk/future"
//	"github.com/algorand/go-algorand-sdk/transaction"
//	"github.com/algorand/go-algorand-sdk/types"
//)
//
//func main() {
//	client, err := algod.MakeClient("http://127.0.0.1:4001", strings.Repeat("a", 64))
//	if err != nil {
//		log.Fatalf("Failed to init client: %+v", err)
//	}
//
//	sp, err := client.SuggestedParams().Do(context.Background())
//	if err != nil {
//		log.Fatalf("Failed to get suggested params: %+v", err)
//	}
//
//	accts, err := GetAccounts()
//	if err != nil {
//		log.Fatalf("Failed to get accounts: %+v", err)
//	}
//
//	lsa := getLogic(client)
//
//	addr, err := lsa.Address()
//	if err != nil {
//		log.Fatalf("Failed to get address for logic: %+v", err)
//	}
//
//	pay_txn, err := future.MakePaymentTxn(accts[1].Address.String(), addr.String(), 10000, nil, "", sp)
//	if err != nil {
//		log.Fatalf("Failed to create payment transaction: %+v", err)
//	}
//
//	app_txn, err := future.MakeApplicationNoOpTx(1, nil, []string{accts[2].Address.String()}, nil, []uint64{}, sp, accts[1].Address, nil, types.Digest{}, [32]byte{}, types.Address{})
//	if err != nil {
//		log.Fatalf("Failed to create app call txn: %+v", err)
//	}
//
//	logic_txn, err := future.MakePaymentTxn(addr.String(), accts[1].Address.String(), 10000, nil, "", sp)
//	if err != nil {
//		log.Fatalf("Failed to create logic transaction: %+v", err)
//	}
//
//	txns, _ := transaction.AssignGroupID([]types.Transaction{
//		pay_txn, app_txn, logic_txn,
//	}, "")
//
//	_, s_pay_bytes, err := crypto.SignTransaction(accts[1].PrivateKey, txns[0])
//	if err != nil {
//		log.Fatalf("Failed to sign pay txn: %+v", err)
//	}
//	s_pay := types.SignedTxn{}
//	msgpack.Decode(s_pay_bytes, &s_pay)
//
//	_, s_app_bytes, err := crypto.SignTransaction(accts[1].PrivateKey, txns[1])
//	if err != nil {
//		log.Fatalf("Failed to sign app txn: %+v", err)
//	}
//	s_app := types.SignedTxn{}
//	msgpack.Decode(s_app_bytes, &s_app)
//
//	_, s_logic_bytes, err := crypto.SignLogicSigAccountTransaction(lsa, txns[2])
//	if err != nil {
//		log.Fatalf("Failed to sign logic txn: %+v", err)
//	}
//	s_logic := types.SignedTxn{}
//	msgpack.Decode(s_logic_bytes, &s_logic)
//
//	drr, err := future.CreateDryrun(client, []types.SignedTxn{s_pay, s_app, s_logic}, nil, context.Background())
//	if err != nil {
//		log.Fatalf("Failed to create dryrun: %+v", err)
//	}
//
//	filename := "go-drr.msgp"
//	os.WriteFile(filename, msgpack.Encode(drr), 0666)
//	log.Printf("Wrote to file: %s", filename)
//}
//
//func getLogic(client *algod.Client) crypto.LogicSigAccount {
//	b, err := os.ReadFile("../logic.teal")
//	if err != nil {
//		log.Fatalf("Failed to read file: %+v", err)
//	}
//
//	res, err := client.TealCompile(b).Do(context.Background())
//	if err != nil {
//		log.Fatalf("Failed to compile program: %+v", err)
//	}
//	b, err = base64.StdEncoding.DecodeString(res.Result)
//	if err != nil {
//		log.Fatalf("Failed to decode program: %+v", err)
//	}
//
//	return crypto.LogicSigAccount{
//		Lsig: types.LogicSig{Logic: b},
//	}
//}
//
