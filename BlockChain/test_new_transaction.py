import requests
from transaction import Transaction, TransactionProcessor
from blockchain import Blockchain
from blockchain_db import BlockchainDB

# Initialize components
db = BlockchainDB(":memory:")
blockchain = Blockchain(difficulty=4, db=db)
tx_processor = TransactionProcessor()

# Create and send a new transaction
tx = tx_processor.create_transaction("Alice", "Bob", 25.0)
blockchain.add_pending_transaction(tx)
blockchain.mine_pending_transactions("miner_address")

# Check the updated state through the API
response = requests.get('http://localhost:5000/balance/Bob')
print("Bob's new balance:", response.json()) 