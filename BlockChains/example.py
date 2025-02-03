from blockchain import Blockchain
from transaction import TransactionProcessor

# Create blockchain
blockchain = Blockchain(difficulty=4)

# Create transaction processor
tx_processor = TransactionProcessor()

# Create some transactions
tx1 = tx_processor.create_transaction("Alice", "Bob", 50.0)
tx2 = tx_processor.create_transaction("Bob", "Charlie", 30.0)

# Add transactions to blockchain
blockchain.add_pending_transaction(tx1)
blockchain.add_pending_transaction(tx2)

# Mine pending transactions
blockchain.mine_pending_transactions("miner_address")

# Check balances
print(f"Bob's balance: {tx_processor.get_balance('Bob', blockchain)}")
print(f"Miner's balance: {tx_processor.get_balance('miner_address', blockchain)}") 