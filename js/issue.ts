import algosdk from 'algosdk'
import fs from 'fs';

(async function (){

    const logic = fs.readFileSync("/home/ben/issue.teal.tok");
    console.log(logic.toString('hex'))

    const lsa = new algosdk.LogicSigAccount(logic)
    console.log(lsa)
    
})()