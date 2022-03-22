import algosdk from 'algosdk'
import {getAccounts} from './sandbox'
import fs from 'fs';

const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const server = 'http://127.0.0.1';
const port = 4001;
const client = new algosdk.Algodv2(token, server, port);


async function dothing(){
    const [acct1, acct2, acct3] = await getAccounts()

    const sp = await client.getTransactionParams().do()
    const pay_txn = algosdk.makePaymentTxnWithSuggestedParams(acct1.addr, acct2.addr, 10000, undefined, undefined, sp)

    console.log(pay_txn)
    const pay_txn_bytes = algosdk.encodeObj(pay_txn.get_obj_for_encoding())
    fs.writeFileSync("pay.txn", Buffer.from(pay_txn_bytes).toString("base64"))

    const spay_txn_bytes = pay_txn.signTxn(acct1.sk)
    fs.writeFileSync("signed_pay.txn", Buffer.from(spay_txn_bytes).toString("base64"))


    const recovered_pay_txn = algosdk.decodeUnsignedTransaction(Buffer.from(fs.readFileSync("pay.txn").toString(), "base64"))
    console.log(recovered_pay_txn)

    const recovered_signed_pay_txn = algosdk.decodeSignedTransaction(Buffer.from(fs.readFileSync("signed_pay.txn").toString(), "base64"))
    console.log(recovered_signed_pay_txn)

}

(async function(){
    await dothing()
})()