package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"strings"

	"github.com/algorand/go-algorand-sdk/client/v2/algod"
	"github.com/algorand/go-algorand-sdk/crypto"
	"github.com/algorand/go-algorand-sdk/future"
	"github.com/algorand/go-algorand-sdk/mnemonic"
	"github.com/algorand/go-algorand-sdk/types"
)

// CHANGE ME
var (
	algodAddress = "http://localhost:4001"
	algodToken   = strings.Repeat("a", 64)
)

func main() {
	// ignore error checking for readability

	addr1, _ := types.DecodeAddress("DN7MBMCL5JQ3PFUQS7TMX5AH4EEKOBJVDUF4TCV6WERATKFLQF4MQUPZTA")
	addr2, _ := types.DecodeAddress("BFRTECKTOOE7A5LHCF3TTEOH2A7BW46IYT2SX5VP6ANKEXHZYJY77SJTVM")

	mn1 := "auction inquiry lava second expand liberty glass involve ginger illness length room item discover ahead table doctor term tackle cement bonus profit right above catch"
	sk1, _ := mnemonic.ToPrivateKey(mn1)

	mn2 := "since during average anxiety protect cherry club long lawsuit loan expand embark forum theory winter park twenty ball kangaroo cram burst board host ability left"
	sk2, _ := mnemonic.ToPrivateKey(mn2)

	ma, _ := crypto.MultisigAccountWithParams(1, 2, []types.Address{
		addr1,
		addr2,
	})

	program := []byte{1, 32, 1, 0, 34} // int 0 => never transfer money
	var args [][]byte
	lsig, _ := crypto.MakeLogicSig(program, args, sk1, ma)
	_ = crypto.AppendMultisigToLogicSig(&lsig, sk2)

	sender, _ := ma.Address()
	_ = crypto.VerifyLogicSig(lsig, sender)

	const receiver = "47YPQTIGQEO7T4Y4RWDYWEKV6RTR2UNBQXBABEEGM72ESWDQNCQ52OPASU"
	const amount = 2000
	var note []byte

	algodClient, _ := algod.MakeClient(algodAddress, algodToken)

	params, err := algodClient.SuggestedParams().Do(context.Background())
	if err != nil {
		return
	}

	tx, _ := future.MakePaymentTxn(sender.String(), receiver, amount, note, "", params)

	txid, stx, err := crypto.SignLogicsigTransaction(lsig, tx)
	if err != nil {
		fmt.Printf("Signing failed with %v", err)
		return
	}
	fmt.Printf("Signed tx: %v\n", txid)

	_, err = algodClient.SendRawTransaction(stx).Do(context.Background())
	if err != nil {
		fmt.Printf("Sending failed with %v\n", err)
	}

	addr := "BH55E5RMBD4GYWXGX5W5PJ5JAHPGM5OXKDQH5DC4O2MGI7NW4H6VOE4CP4"                              // the account issuing the transaction; the asset creator
	fee := types.MicroAlgos(10)                                                                       // the number of microAlgos per byte to pay as a transaction fee
	defaultFrozen := false                                                                            // whether user accounts will need to be unfrozen before transacting
	genesisHash, _ := base64.StdEncoding.DecodeString("SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=") // hash of the genesis block of the network to be used
	totalIssuance := uint64(100)                                                                      // total number of this asset in circulation
	decimals := uint64(1)                                                                             // hint to GUIs for interpreting base unit
	reserve := addr                                                                                   // specified address is considered the asset reserve (it has no special privileges, this is only informational)
	freeze := addr                                                                                    // specified address can freeze or unfreeze user asset holdings
	clawback := addr                                                                                  // specified address can revoke user asset holdings and send them to other addresses
	manager := addr                                                                                   // specified address can change reserve, freeze, clawback, and manager
	unitName := "tst"                                                                                 // used to display asset units to user
	assetName := "testcoin"                                                                           // "friendly name" of asset
	genesisID := ""                                                                                   // like genesisHash this is used to specify network to be used
	firstRound := types.Round(322575)                                                                 // first Algorand round on which this transaction is valid
	lastRound := types.Round(322575)                                                                  // last Algorand round on which this transaction is valid
	note := nil                                                                                       // arbitrary data to be stored in the transaction; here, none is stored
	assetURL := "http://someurl"                                                                      // optional string pointing to a URL relating to the asset
	assetMetadataHash := "thisIsSomeLength32HashCommitment"                                           // optional hash commitment of some sort relating to the asset. 32 character length.

	params := types.SuggestedParams{
		Fee:             fee,
		FirstRoundValid: firstRound,
		LastRoundValid:  lastRound,
		GenesisHash:     genesisHash,
		GenesisID:       genesisID,
	}

	// signing and sending "txn" allows "addr" to create an asset
	txn, err = MakeAssetCreateTxn(addr, note, params,
		totalIssuance, decimals, defaultFrozen, manager, reserve, freeze, clawback,
		unitName, assetName, assetURL, assetMetadataHash)
}
