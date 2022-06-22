#curl -X GET "https://mainnet-algorand.api.purestake.io/idx2/v2/accounts?limit=50&asset-id=701273234&exclude=as" -H "x-api-key:<API_KEY>"

from algosdk.v2client import indexer

token = ""
#host = "https://mainnet-idx.algonode.cloud"
host = "https://algoindexer.algoexplorerapi.io"
client = indexer.IndexerClient(token, host)


total_accts = 0
next_token = None
while True:
    result = client.asset_balances(asset_id=701273234, limit=100, min_balance=0, next_page=next_token)

    if 'next-token' in result:
        next_token=result['next-token']

    if len(result['balances']) == 0:
        break

    print("Up to {}".format(total_accts))

    total_accts += len(result['balances'])

print("Total accounts: {}".format(total_accts))
