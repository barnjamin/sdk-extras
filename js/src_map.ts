import algosdk, { SourceMap } from 'algosdk'
import fs from 'fs';

const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const server = 'http://127.0.0.1';
const port = 4001;
const client = new algosdk.Algodv2(token, server, port);

(async function(){
    const m = JSON.parse(fs.readFileSync("myprog.teal.tok.map").toString())
    const sm = new SourceMap({...m})
    console.log(sm.getLineForPc(2))
})()