import algosdk, { Transaction, TransactionType } from 'algosdk'
import {getAccounts} from './sandbox'
import fs from 'fs';
import { removeUndefinedProperties } from 'algosdk/dist/types/src/utils/utils';

const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const server = 'http://127.0.0.1';
const port = 4001;
const client = new algosdk.Algodv2(token, server, port);

async function generateDryrun(){

    const accts = await getAccounts()
    const lsa = await getLogicSig()

    const sp = await client.getTransactionParams().do()

    const pay_txn = algosdk.makePaymentTxnWithSuggestedParams(
        accts[2].addr, lsa.address(), 10000, undefined, undefined, sp
    )

    const app_txn = algosdk.makeApplicationNoOpTxn(accts[1].addr, sp, 1, undefined, [], [1])

    const logic_txn = algosdk.makePaymentTxnWithSuggestedParams(
         lsa.address(), accts[2].addr, 10000, undefined, undefined, sp
    )

    algosdk.assignGroupID([pay_txn, app_txn, logic_txn])
    const s_pay = algosdk.signTransaction(pay_txn, accts[2].sk)
    const s_app = algosdk.signTransaction(app_txn, accts[2].sk)
    const s_logic = algosdk.signLogicSigTransaction(logic_txn, lsa)


    const drr = await algosdk.createDryrun({
        client: client, 
        txns: [
            algosdk.decodeSignedTransaction(s_pay['blob']), 
            algosdk.decodeSignedTransaction(s_app['blob']),
            algosdk.decodeSignedTransaction(s_logic['blob'])
        ]
    })

    const drres = await client.dryrun(drr).do()
    console.log(drres)

    const filename = 'js-drr.msgp'
    fs.writeFileSync(filename, algosdk.encodeObj(drr.get_obj_for_encoding(true)))

    //const x = new algosdk.DryrunResult(undefined)
    //console.log("Wrote to "+filename)
}

async function getLogicSig(): Promise<algosdk.LogicSigAccount> {
    const logic = fs.readFileSync("../logic.teal");
    const result = await client.compile(logic).do()
    return new algosdk.LogicSigAccount(Buffer.from(result['result'], 'base64'))
}

(async function(){
    await generateDryrun()
})()
