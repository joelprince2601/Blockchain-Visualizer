import unittest
import time
from blockchain import Blockchain
from transaction import Transaction
from data_formatter import BlockchainFormatter
from blockchain_db import BlockchainDB

class TestVisualizationPerformance(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain(difficulty=2)
        self.db = BlockchainDB(":memory:")  # Use in-memory SQLite for testing
        self.formatter = BlockchainFormatter(self.blockchain, self.db)

    def create_test_blockchain(self, num_blocks: int):
        """Create a test blockchain with specified number of blocks"""
        for i in range(num_blocks):
            tx = Transaction(f"User{i}", f"User{i+1}", 1.0)
            self.blockchain.add_pending_transaction(tx)
            self.blockchain.mine_pending_transactions("miner")

    def test_graph_formatting_performance(self):
        """Test performance of graph data formatting"""
        block_counts = [10, 100, 1000]
        
        for count in block_counts:
            self.create_test_blockchain(count)
            
            start_time = time.time()
            graph_data = self.formatter.format_for_graph()
            end_time = time.time()
            
            formatting_time = end_time - start_time
            print(f"Graph formatting time for {count} blocks: {formatting_time:.2f}s")
            
            # Format time should be reasonable
            self.assertLess(formatting_time, count * 0.01)  # 10ms per block max

    def test_transaction_flow_performance(self):
        """Test performance of transaction flow formatting"""
        self.create_test_blockchain(100)
        
        start_time = time.time()
        flow_data = self.formatter.format_transaction_flow()
        end_time = time.time()
        
        formatting_time = end_time - start_time
        print(f"Transaction flow formatting time: {formatting_time:.2f}s")
        
        # Should format within 1 second
        self.assertLess(formatting_time, 1.0) 