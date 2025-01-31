from pymongo import MongoClient
from urllib.parse import quote_plus
from top_wallet import getTopWallets, getTopPair
import time
from datetime import datetime
# Replace these with your actual username and password
username = 'blackhole'
password = 'pwd123!@#'

# URL-encode the username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Construct the MongoDB URI using the encoded values
MONGODB_URI = f'mongodb+srv://{encoded_username}:{encoded_password}@cluster0.lcx3d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
# MONGODB_URI = "localhost:27017"

client = MongoClient(MONGODB_URI)
db = client.wallet_monitor
wallets_collection = db.wallets

def test_connection():
  while True:
    top_wallets =  getTopWallets(500000)
    print(f"Top wallets: {len(top_wallets)}")  # Debugging line
    if len(top_wallets) > 2:
      top_wallets = top_wallets[:20]
      if top_wallets:  # Check if top_wallets is not empty
        wallets_collection.delete_many({})
        wallets_collection.insert_many(top_wallets)
        print(f"Inserted {len(top_wallets)} wallets into the collection.{datetime.now().isoformat()}")
      else:
        print("No wallets to insert.")
    time.sleep(3600)

if __name__ == '__main__':
  test_connection()
