from bs4 import BeautifulSoup
import tls_client
import json
import re
from datetime import datetime
import requests

session = tls_client.Session(client_identifier="chrome_105")
headers: dict = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'priority': 'u=1, i',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}
cookies: dict = {
     '_photon_ta': 'xV%2BUrZ9XP2PiC0ZjNpXFL206tgfzoHoHmGMOXaY32XAxjx0b1gD8blQoABfmUhCferPySNXl9Kk0STrUMp7s91BKE7c7YAMiY7uOEiTvPoXWq%2FnuOVY1rhYXIugUQHLlhhHc1STfCpGFweUOsLGobDbYJaL6GshRcnA7prIpAr6Z2zbJARjoQVrhSx%2BZN2JINjTwe0NRrWePpC64rKoA4Yl5MODB4ICRzZeVB2zqFhS9q%2FkriIri6WZrPIEDgKJM%2FkySqVrR2n4IOnYGsCfgnZWnjRWWcijiPiMFdONbCt0NJAlW%2FE2bLwcj75aVMY1RkDLnH787UOhb1N%2BRr9nFM0RQk4Ev7Vz6874WqKmkwfsMmEkoL0h1BUzeoc1JCdHHs1NkF%2F1cSsetAY%2BadDHLkOxaqC5APr20EepSaGl91r0NPobCqPaXCcrSbES3MaQ9SU3ajrb7ON2J3K9yQ4%2BG%2BSFixESkbATFYFaxmtkTLXbKUf3e23AQRkY2%2F0ioTAl8Wl%2FoffFq7AO04A2VuR38oJpoBDJ8bHNusiFLHvIiht%2F%2FwDsxzmI2vkRYBgGN%2Fpfyyq2eWQ%3D%3D--vGdbkA7OaNghlUdj--uw1aOR7SQn7M3IPnG6nREg%3D%3D'
}

def getPairByCA(contractAddress: str) -> str:
    getPairCA = session.get(f"https://photon-sol.tinyastro.io/en/lp/{contractAddress}", headers=headers).text
    soup = BeautifulSoup(getPairCA, "html.parser")
    pair = soup.find('a')['href'].replace("//", "/")

    return pair

def getPoolID(pair: str):
    getPoolID = session.get(f"https://photon-sol.tinyastro.io/en/{pair}", headers=headers).text
    soup = BeautifulSoup(getPoolID, "html.parser").find('script', string=re.compile(r'window\.taConfig.show')).string
    poolMatch = re.search(r"'pool-id': (\d+)", soup)
    pool_id = poolMatch.group(1)

    return pool_id

def getTopPair():
    url = 'https://photon-sol.tinyastro.io/api/trending?age_from=6000&dexes=raydium%2Cpump%2Cmoonshot%2Cmemelive%2Corca%2Cmeteora&extra_filters_count=1&order_by=volume&order_dir=desc&period=1h&quick_snipe=true'
    updated_cookies = session.cookies
    
    response = requests.get(url, headers=headers, cookies=updated_cookies) 
    print('-----------------------------------', response)
    soup = BeautifulSoup(response.content, "html.parser")
    top_pair_urls = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs and a['href'].startswith('/app/solana/chart')]
    top_pair_urls = top_pair_urls[:20]
    return top_pair_urls

def getTopWallets(pnl_limit):

    top_trader_500k_length:int = 0
    allData: dict = {}

    with open('tokens.txt', 'r') as fp:

        pool_id = 12883711
        grabTopTradersURL = f"https://photon-sol.tinyastro.io/api/events/top_traders?order_by=timestamp&order_dir=desc&pool_id={pool_id}&page=1"

        response = session.get(grabTopTradersURL, headers=headers, cookies=cookies).json()
        updated_cookies = session.cookies
        # print('first ---- updated_cookies', updated_cookies)
        
        # contractAddresses = fp.read().splitlines()
    
    url = 'https://photon-sol.tinyastro.io/api/trending?age_from=6000&dexes=raydium%2Cpump%2Cmoonshot%2Cmemelive%2Corca%2Cmeteora&extra_filters_count=1&order_by=volume&order_dir=desc&period=1h&quick_snipe=true'
    updated_cookies = session.cookies
    response = session.get(url, headers=headers, cookies=updated_cookies).json()
    # print('---------------', response.json())
    pair_ids = list()
         
    # Sort the data by volume in descending order
    sorted_data = sorted(response['data'], key=lambda x: x['volume'], reverse=True)

    for index, topPair in enumerate(sorted_data):
        print('volume',topPair['volume'])
        pair_ids.append(topPair['id'])
    pair_ids = pair_ids[:20]

    top_trader_addresses = list()
    for pair_id in pair_ids:
        # pair = getPairByCA(contractAddress)
        # pool_id = getPoolID(pair)
        grabTopTradersURL = f"https://photon-sol.tinyastro.io/api/events/top_traders?page=1&order_by=timestamp&order_dir=dir&pool_id={pair_id}"
           
        print('line 47: new cookie-->', pair_id)
        updated_cookies = session.cookies
        response = session.get(grabTopTradersURL, headers=headers, cookies=updated_cookies).json()
        allData[pair_id] = {}

        for index, topTrader in enumerate(response['data']):
            signer = topTrader['attributes']['signer']
            pnl = float(topTrader['attributes']['plUsd'])
            Volumn = float(topTrader['attributes']['boughtToken'])
            
            if pnl > pnl_limit:
                print('response---------------------------------',pnl)
                top_trader_addresses.append({
                    'address': signer,
                    'name': f"wallet{index + 1}",
                    'pnl': pnl,
                    'Volumn': Volumn,
                    'last_signatures': [],
                    'recent_update': datetime.now().isoformat()
                })
                top_trader_500k_length+=1
    return top_trader_addresses
    # with open('top_traders.json', 'w') as fp:
    #     json.dump(top_trader_addresses, fp, indent=4)

# if __name__ == "__main__":
#     pnl_limit = 500000
#     main(pnl_limit)
