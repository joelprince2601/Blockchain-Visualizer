from blockchain import Blockchain
from blockchain_db import BlockchainDB
from transaction import Transaction, TransactionProcessor
import time

def main():
    # Initialize components
    db = BlockchainDB("blockchain.db")
    blockchain = Blockchain(difficulty=4, db=db)
    tx_processor = TransactionProcessor()

    # Create some test transactions
    transactions = [
        ("Alice", "Bob", 50.0),
        ("Bob", "Charlie", 30.0),
        ("Charlie", "Alice", 20.0)
    ]

    # Process transactions
    for sender, recipient, amount in transactions:
        tx = tx_processor.create_transaction(sender, recipient, amount)
        blockchain.add_pending_transaction(tx)
        print(f"Created transaction: {sender} -> {recipient}: {amount} coins")

    # Mine the transactions
    print("\nMining pending transactions...")
    blockchain.mine_pending_transactions("miner_address")
    print("Mining completed!")

    # Check balances
    addresses = ["Alice", "Bob", "Charlie", "miner_address"]
    print("\nFinal balances:")
    for address in addresses:
        balance = tx_processor.get_balance(address, blockchain)
        print(f"{address}: {balance} coins")

if __name__ == "__main__":
    main() 