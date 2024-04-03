import requests
import pandas as pd
import schedule
import time
import os
from datetime import datetime

def query_liquidity_pools_api(chain_selection='solana'):
    # Adjust the URL and parameters as needed to fetch new pools data
    url = f"https://api.geckoterminal.com/api/v2/networks/{chain_selection}/new_pools?include=base_token%2Cquote_token&page=5"
    response = requests.get(url)
    print("Querying...")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error querying liquidity pools API: {response.status_code}")
        return []

def query_detailed_token_info(token_address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # Assuming this always returns a dictionary
            # Check if 'pairs' is None and replace it with an empty list if so
            if data.get('pairs') is None:
                data['pairs'] = []
            return data
        else:
            print(f"Failed to query detailed token info, status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while querying detailed token info: {str(e)}")
    # Return a default structure if the request fails or in case of exception
    return {'pairs': []}

def filter_tokens(pools):
    filtered_tokens_with_all_criteria = []
    filtered_tokens_excluding_some_criteria = []
    for pool in pools:
        token_address = pool['attributes']['address']
        detailed_info = query_detailed_token_info(token_address)
        for pair in detailed_info.get('pairs', []):
                if pair['liquidity']['usd'] > 1000 and \
                   pair['fdv'] > 5000 and \
                   pair['priceChange']['h24'] > -50:
                   
                    # Token data structure for the second database (excluding some criteria)
                    token_data_excluding_some_criteria = {
                        'name': pool['attributes']['name'],
                        'address': "https://dexscreener.com/solana/" + token_address,
                        'liquidity_usd': pair['liquidity']['usd'],
                        'fdv': pair['fdv'],
                        'priceChange_h24': pair['priceChange']['h24']
                    }
                    filtered_tokens_excluding_some_criteria.append(token_data_excluding_some_criteria)
                    
                    # Check for presence of 'imageUrl', 'websites', and 'socials'
                    if 'info' in pair and \
                       pair['info'].get('imageUrl') and \
                       pair['info'].get('websites') and len(pair['info']['websites']) > 0 and \
                       pair['info'].get('socials') and len(pair['info']['socials']) > 0:
                       
                        # Token data structure for the first database (with all criteria)
                        filtered_tokens_with_all_criteria.append(token_data_excluding_some_criteria)
                        
    return filtered_tokens_with_all_criteria, filtered_tokens_excluding_some_criteria

def write_to_csv(filtered_tokens, file_path):
    file_exists = os.path.isfile(file_path)
    
    # Add a timestamp to each token record
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for token in filtered_tokens:
        token['timestamp'] = timestamp
    
    new_tokens_df = pd.DataFrame(filtered_tokens)
    
    if not file_exists or os.stat(file_path).st_size == 0:
        header = True
    else:
        header = False
        existing_df = pd.read_csv(file_path)
        # Adjust to also check the timestamp if you want to avoid duplicates within the same timestamp
        new_tokens_df = new_tokens_df[~new_tokens_df['address'].isin(existing_df['address'])]

    if not new_tokens_df.empty:
        new_tokens_df.to_csv(file_path, mode='a', header=header, index=False)

def collect_and_filter_data():
    pools = query_liquidity_pools_api('solana')  # Adjust as needed
    if pools:
        tokens_with_all_criteria, tokens_excluding_some_criteria = filter_tokens(pools.get('data', []))
        if tokens_with_all_criteria:
            write_to_csv(tokens_with_all_criteria, 'C:/Users/Patrik/Coding/crypto/patrik_bot/New Pools Tool/token_database.csv')
        if tokens_excluding_some_criteria:
            write_to_csv(tokens_excluding_some_criteria, 'C:/Users/Patrik/Coding/crypto/patrik_bot/New Pools Tool/token_database_all.csv')

def filter_recent_tokens(file_path, hours=24):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    cutoff_time = datetime.now() - pd.Timedelta(hours=hours)
    recent_tokens_df = df[df['timestamp'] > cutoff_time]
    return recent_tokens_df

# Scheduling the data collection to run 20 times per minute
schedule.every(3).seconds.do(collect_and_filter_data)

while True:
    schedule.run_pending()
    time.sleep(1)


if __name__ == "__main__":
    print("hello")
    # result = query_detailed_token_info()