from datetime import datetime
import hashlib
from typing import List, Any
import time

class Block:
    def __init__(self, index: int, transactions: List[Any], previous_hash: str, 
                 timestamp: float = None, nonce: int = 0, hash: str = None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()
        self.difficulty = 4  # Number of leading zeros required in hash

    def calculate_hash(self) -> str:
        """Calculate the hash of the block using SHA-256"""
        block_content = (
            str(self.index) +
            str(self.timestamp) +
            str(self.transactions) +
            str(self.previous_hash) +
            str(self.nonce)
        )
        return hashlib.sha256(block_content.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """Mine the block by finding a hash with specified number of leading zeros"""
        self.difficulty = difficulty
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> dict:
        """Convert block to dictionary format"""
        return {
            'index': self.index,
            'timestamp': datetime.fromtimestamp(self.timestamp).isoformat(),
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce
        } 