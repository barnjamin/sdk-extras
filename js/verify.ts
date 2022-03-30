import algosdk, { makePaymentTxn, makePaymentTxnWithSuggestedParamsFromObject, SignedTransaction, SuggestedParams } from 'algosdk'
import { getAccounts } from './sandbox'
import nacl from 'tweetnacl'

function verifySignedTransaction(stxn: SignedTransaction){

    if (stxn.sig === undefined) return false;

    const pk_bytes = stxn.txn.from.publicKey

    const sig_bytes = new Uint8Array(stxn.sig);

    const txn_bytes = algosdk.encodeObj(stxn.txn.get_obj_for_encoding())
    const msg_bytes = new Uint8Array(txn_bytes.length + 2)
    msg_bytes.set(Buffer.from("TX"))
    msg_bytes.set(txn_bytes, 2)

    return nacl.sign.detached.verify(msg_bytes, sig_bytes, pk_bytes);

}

(function(){
    const sp: SuggestedParams = {fee: 0, firstRound: 1, lastRound:2, genesisHash:"nDtgfcrOMvfAaxYZSL+gCqA2ot5uBknFJuWE4pVFloo=", genesisID:"sandnet-v1"} 
    const acct = algosdk.generateAccount()
    const txn = makePaymentTxnWithSuggestedParamsFromObject({
        from: acct.addr,
        to: acct.addr,
        amount: 0,
        suggestedParams: sp,
    })

    const blob = txn.signTxn(acct.sk)

    const stxn = algosdk.decodeSignedTransaction(blob)
    console.log("Valid? ", verifySignedTransaction(stxn))
})()