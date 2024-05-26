import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time
from datetime import datetime


load_dotenv()

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
HOT_WALLET_ADDRESS = os.getenv('HOT_WALLET_ADDRESS')
THRESHOLD_VALUE = 1  
CHECK_INTERVAL = 300  
PRICE_CHECK_INTERVAL = 60  
PRICE_MONITOR_DURATION = 30 * 60  

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

def get_eth_price():
    url = f"https://api.etherscan.io/api"
    params = {
        'module': 'stats',
        'action': 'ethprice',
        'apikey': ETHERSCAN_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == '1':
        return float(data['result']['ethusd'])
    else:
        print("Error fetching Ethereum price:", data['message'])
        return None

def parse_transactions(transactions, threshold=THRESHOLD_VALUE):
    trades = []
    for tx in transactions:
        value_eth = int(tx['value']) / 10**18  
        if value_eth >= threshold:
            trade = {
                'blockNumber': tx['blockNumber'],
                'timeStamp': pd.to_datetime(tx['timeStamp'], unit='s'),
                'hash': tx['hash'],
                'from': tx['from'],
                'to': tx['to'],
                'value': value_eth,
                'gas': tx['gas'],
                'gasPrice': int(tx['gasPrice']) / 10**9, 
                'isError': tx['isError'],
                'txreceipt_status': tx['txreceipt_status']
            }
            trades.append(trade)
    return trades

def display_trades(trades):
    df = pd.DataFrame(trades)
    print(df)
    return df

def monitor_eth_price(duration, interval, log_file):
    start_time = time.time()
    end_time = start_time + duration
    
    with open(log_file, 'a') as f:
        f.write(f"\nMonitoring ETH price for {duration//60} minutes from {datetime.now()}\n")
        while time.time() < end_time:
            price = get_eth_price()
            if price is not None:
                log_entry = f"{datetime.now()}: ${price}\n"
                print(log_entry.strip())
                f.write(log_entry)
            else:
                log_entry = f"{datetime.now()}: Error fetching price\n"
                print(log_entry.strip())
                f.write(log_entry)
            time.sleep(interval)

if __name__ == "__main__":
    while True:
        transactions = get_transactions(HOT_WALLET_ADDRESS)
        

        print(f"Total transactions fetched: {len(transactions)}")
        print(transactions[:5])  
        
        trades = parse_transactions(transactions)
        df_trades = display_trades(trades)
        
        if not df_trades.empty:
            log_file = "eth_price_log.txt"
            monitor_eth_price(PRICE_MONITOR_DURATION, PRICE_CHECK_INTERVAL, log_file)
        

        time.sleep(CHECK_INTERVAL)
