from typing import List, Optional
from block import Block
from transaction import Transaction
from blockchain_db import BlockchainDB
from security import BlockchainSecurity
from transaction_processor import TransactionProcessor

class Blockchain:
    def __init__(self, difficulty: int = 4, db: Optional[BlockchainDB] = None):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = 10.0
        self.db = db
        self.transaction_processor = TransactionProcessor()
        
        # If we have a database, load the existing chain or create genesis block
        if self.db:
            existing_blocks = self.db.get_all_blocks()
            if existing_blocks:
                # Convert dictionary blocks to Block objects
                self.chain = [Block(
                    block['block_index'],
                    block['transactions'],
                    block['previous_hash'],
                    block['timestamp'],
                    block['nonce'],
                    block['hash']
                ) for block in existing_blocks]
            else:
                self._create_genesis_block()
        else:
            self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Return the most recent block in the chain"""
        return self.chain[-1]

    def add_block(self, transactions: List[Transaction]) -> Block:
        """Create a new block and add it to the chain"""
        new_block = Block(
            len(self.chain),
            transactions,
            self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        
        # Save to database if available
        if self.db:
            # Convert the block to a format suitable for database storage
            block_data = {
                'block_index': new_block.index,
                'transactions': new_block.transactions,
                'previous_hash': new_block.previous_hash,
                'timestamp': str(new_block.timestamp),
                'nonce': new_block.nonce,
                'hash': new_block.hash
            }
            if isinstance(block_data, dict):
                block_data = Block(
                    index=block_data['block_index'],
                    timestamp=block_data['timestamp'],
                    transactions=block_data['transactions'],
                    previous_hash=block_data['previous_hash'],
                    nonce=block_data['nonce']
                )
            self.db.save_block(block_data)
        
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                return False

        return True 

    def add_pending_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to pending transactions"""
        if self.transaction_processor.validate_transaction(transaction):
            self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address: str) -> None:
        """
        Mine pending transactions and create a new block
        Reward is sent to miner_address
        """
        # Create mining reward transaction
        reward_transaction = Transaction(
            "System",
            miner_address,
            self.mining_reward
        )

        # Add reward transaction to pending transactions
        self.pending_transactions.append(reward_transaction)

        # Create new block with all pending transactions
        new_block = self.add_block(self.pending_transactions)
        
        # Clear pending transactions
        self.pending_transactions = []

    def verify_block(self, block: Block) -> bool:
        """Verify a block received from peers"""
        return BlockchainSecurity.verify_block_integrity(block)

    def add_block_from_peer(self, block: Block) -> bool:
        """Add a verified block from a peer"""
        if self.verify_block(block) and block.previous_hash == self.get_latest_block().hash:
            self.chain.append(block)
            return True
        return False

    def verify_transaction(self, transaction: Transaction) -> bool:
        """Verify a transaction before adding to pending"""
        return (
            BlockchainSecurity.verify_transaction_signature(transaction) and
            BlockchainSecurity.detect_double_spending(self.chain, transaction)
        )