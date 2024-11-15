# PocketCoin Spy by James Lawrence
#
# Filename: pcspy.py
# Version: 0.0.1
# Date: 3 Nov 2024
#
# A Script to show each stake reward from a given day
#
# Example: python3 pcspy.py 2024-01-31
#
# Freely use or distribute this code. No warrenties of any kind. Use at your own risk
# Requires Python 3.9 (It might work on downlevel versions)

import requests, sys, configparser
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def get_address_transactions(url, address, page=1, page_size=999999):
    
    latestblock = str(get_last_blocks(url))
    
    params = {
        "method": "getaddresstransactions",
        "params": [
            address, # Your address
            latestblock, # Top block height for starting pagination
            page, # Start page number
            page_size, # Page size
            1, # Direction transactions (-1: outgoing, 1: incoming, 0: both)
            3 # Type of transaction. 1 - stacking, 
        ]
    }
    response = requests.post(url, json=params)
    data = response.json()

    formatted_transactions = []
    for transaction in data['result']:
        #print(transaction)
        if 'height' not in transaction:
            continue
        formatted_transactions.append(format_transactions(address, transaction))

    return formatted_transactions

def format_transactions(address, transaction):
    amount_input = sum(vin['value'] for vin in transaction['vin'])
    amount_final = sum(vout['value'] for vout in transaction['vout'] if vout['scriptPubKey']['addresses'][0] == address)
    amount = amount_final - amount_input
    return {
        "txid": transaction['txid'],
        "type": transaction['type'],
        "height": transaction['height'],
        "nTime": datetime.utcfromtimestamp(transaction['nTime']).strftime("%Y-%m-%d %H:%M:%S"),
        "amount": amount
    }

def get_last_blocks(url):
    params = {
            "method": "getlastblocks",
            "params": [
                1, # Direction transactions (-1: outgoing, 1: incoming, 0: both)
            ]
        }
    response = requests.post(url, json=params)
    data = response.json()
    
    return{data['result'][0]['height']}

#Load Settings
config = configparser.ConfigParser()

config.read('pcspy.conf')
url = config['main']['url']
address = config['main']['address']
tz = config['main']['tz']

localtime = ZoneInfo(tz)

if len(sys.argv) != 2:
        print()
        print("******************* pcspy.py ******************") 
        print()
        print("pcspy.py returns all of stake rewards for a specified date")
        print()
        print("exacly one option is required which is the date to return stake rewards for in the format of YYYY-mm-dd")
        print()
        print("Example: python3 pcspy.py 2024-01-31")
        print()
        exit()

checkdate = sys.argv[1]

transactions = get_address_transactions(url, address)
totalamt = 0
print()
print("Listing transactions for " + checkdate)
print()
print()

for transaction in transactions:        
    datetime_object = datetime.strptime(transaction['nTime'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    datetimestring = datetime_object.astimezone(localtime).strftime("%Y-%m-%d %H:%M:%S")
    dateonlystring = datetimestring[0:10]
    if dateonlystring == checkdate:
        totalamt = totalamt + transaction['amount']
        print(f"{transaction['txid']}\t{transaction['type']}\t{transaction['height']}\t{datetime_object.astimezone(localtime)}\t{round(transaction['amount'], 8):.8f}")
print()
rndtotalamt = round(totalamt, 8)
print(f'Total: {rndtotalamt:.8f}')
