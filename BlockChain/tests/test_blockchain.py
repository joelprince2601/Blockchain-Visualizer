import unittest
from datetime import datetime
import time
from blockchain import Blockchain
from block import Block
from transaction import Transaction, TransactionProcessor
from blockchain_db import BlockchainDB

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain(difficulty=2)  # Lower difficulty for faster tests
        self.tx_processor = TransactionProcessor()

    def test_genesis_block(self):
        """Test genesis block creation"""
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(len(genesis.transactions), 0)

    def test_add_block(self):
        """Test adding new blocks"""
        tx = Transaction("Alice", "Bob", 50.0)
        self.blockchain.add_pending_transaction(tx)
        initial_length = len(self.blockchain.chain)
        
        self.blockchain.mine_pending_transactions("miner")
        
        self.assertEqual(len(self.blockchain.chain), initial_length + 1)
        self.assertTrue(self.blockchain.is_chain_valid())

    def test_chain_validity(self):
        """Test blockchain validity checks"""
        # Add some blocks
        tx1 = Transaction("Alice", "Bob", 50.0)
        tx2 = Transaction("Bob", "Charlie", 30.0)
        
        self.blockchain.add_pending_transaction(tx1)
        self.blockchain.mine_pending_transactions("miner")
        
        self.blockchain.add_pending_transaction(tx2)
        self.blockchain.mine_pending_transactions("miner")
        
        # Verify chain is valid
        self.assertTrue(self.blockchain.is_chain_valid())
        
        # Tamper with a block
        self.blockchain.chain[1].transactions[0].amount = 100.0
        
        # Verify chain is now invalid
        self.assertFalse(self.blockchain.is_chain_valid())

    def test_mining_reward(self):
        """Test mining rewards"""
        miner_address = "miner1"
        
        # Mine some blocks
        tx = Transaction("Alice", "Bob", 50.0)
        self.blockchain.add_pending_transaction(tx)
        self.blockchain.mine_pending_transactions(miner_address)
        
        # Check miner's balance
        miner_balance = self.tx_processor.get_balance(miner_address, self.blockchain)
        self.assertEqual(miner_balance, self.blockchain.mining_reward)

class TestBlockchainPerformance(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain(difficulty=3)
        self.tx_processor = TransactionProcessor()

    def test_mining_performance(self):
        """Test mining performance"""
        tx = Transaction("Alice", "Bob", 50.0)
        self.blockchain.add_pending_transaction(tx)
        
        start_time = time.time()
        self.blockchain.mine_pending_transactions("miner")
        end_time = time.time()
        
        mining_time = end_time - start_time
        print(f"Mining time: {mining_time:.2f} seconds")
        
        # Mining should take less than 5 seconds with difficulty=3
        self.assertLess(mining_time, 5.0)

    def test_transaction_throughput(self):
        """Test transaction processing throughput"""
        num_transactions = 100
        start_time = time.time()
        
        # Create and process multiple transactions
        for i in range(num_transactions):
            tx = Transaction(f"User{i}", f"User{i+1}", 1.0)
            self.blockchain.add_pending_transaction(tx)
        
        self.blockchain.mine_pending_transactions("miner")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        throughput = num_transactions / processing_time
        print(f"Transaction throughput: {throughput:.2f} tx/s")
        
        # Should process at least 10 transactions per second
        self.assertGreater(throughput, 10.0) 