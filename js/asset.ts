import algosdk from 'algosdk'
import {getAccounts} from './sandbox'
import fs from 'fs';

const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const server = 'http://127.0.0.1';
const port = 4001;
const client = new algosdk.Algodv2(token, server, port);


async function dothing(){

    const asset_id = 13
    const assetReq = client.getAssetByID(asset_id)


    const assetDetails = await assetReq.do()

    const x = BigInt(18446744073709551615)
    console.log(x)

    console.log(BigInt(assetDetails.params.total))
    //console.log(assetDetails.params.total - 10)
    //console.log(assetDetails.params.total - 10000)
    //console.log(assetDetails)

}

(async function(){
    await dothing()
})()