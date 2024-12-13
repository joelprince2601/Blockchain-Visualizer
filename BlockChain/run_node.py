from blockchain import Blockchain
from blockchain_db import BlockchainDB
from network_node import BlockchainNode
from transaction import TransactionProcessor
import time

def main():
    # Initialize components
    db = BlockchainDB()
    blockchain = Blockchain(difficulty=4, db=db)
    tx_processor = TransactionProcessor()
    
    # Create and start node
    node = BlockchainNode(5000, blockchain)
    node.start()
    
    print("Blockchain node started on port 5000")
    print("Mining is", "enabled" if node.mining else "disabled")
    
    try:
        while True:
            # Keep the main thread alive
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down node...")

if __name__ == "__main__":
    main() 