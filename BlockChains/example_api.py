from blockchain import Blockchain
from blockchain_db import BlockchainDB
from transaction import TransactionProcessor
import requests

# Initialize components
db = BlockchainDB()
blockchain = Blockchain(difficulty=4, db=db)
tx_processor = TransactionProcessor()

# Create and mine some transactions
tx1 = tx_processor.create_transaction("Alice", "Bob", 50.0)
blockchain.add_pending_transaction(tx1)
blockchain.mine_pending_transactions("miner_address")

# Start the Flask server (run api.py)

# Make API requests
def test_api():
    # Get all blocks
    response = requests.get('http://localhost:5000/blocks')
    print("All blocks:", response.json())

    # Get specific block
    response = requests.get('http://localhost:5000/blocks/0')
    print("Genesis block:", response.json())

    # Get balance
    response = requests.get('http://localhost:5000/balance/Bob')
    print("Bob's balance:", response.json())

    # Get chain status
    response = requests.get('http://localhost:5000/chain/status')
    print("Chain status:", response.json())

if __name__ == '__main__':
    test_api() 