import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
HOT_WALLET_ADDRESS = os.getenv('HOT_WALLET_ADDRESS')

def get_transactions(address):
    url = f"https://api.etherscan.io/api"
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': ETHERSCAN_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == '1':
        return data['result']
    else:
        print("Error fetching transactions:", data['message'])
        return []

def parse_transactions(transactions):
    trades = []
    for tx in transactions:
        trade = {
            'blockNumber': tx['blockNumber'],
            'timeStamp': pd.to_datetime(tx['timeStamp'], unit='s'),
            'hash': tx['hash'],
            'from': tx['from'],
            'to': tx['to'],
            'value': int(tx['value']) / 10**18,
            'gas': tx['gas'],
            'gasPrice': int(tx['gasPrice']) / 10**9,  # Convert from wei to gwei
            'isError': tx['isError'],
            'txreceipt_status': tx['txreceipt_status']
        }
        trades.append(trade)
    return trades

def display_trades(trades):
    df = pd.DataFrame(trades)
    print(df)

if __name__ == "__main__":
    transactions = get_transactions(HOT_WALLET_ADDRESS)
    trades = parse_transactions(transactions)
    display_trades(trades)
