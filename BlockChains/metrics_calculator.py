from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
from blockchain import Blockchain
from blockchain_db import BlockchainDB

class BlockchainMetrics:
    def __init__(self, blockchain: Blockchain, db: BlockchainDB):
        self.blockchain = blockchain
        self.db = db

    def calculate_basic_metrics(self) -> Dict[str, Any]:
        """Calculate basic blockchain metrics"""
        total_blocks = len(self.blockchain.chain)
        total_transactions = sum(len(block.transactions) for block in self.blockchain.chain)
        
        # Calculate average block time
        if total_blocks > 1:
            time_diff = self.blockchain.chain[-1].timestamp - self.blockchain.chain[0].timestamp
            avg_block_time = time_diff.total_seconds() / (total_blocks - 1)
        else:
            avg_block_time = 0

        return {
            'total_blocks': total_blocks,
            'total_transactions': total_transactions,
            'average_block_time': avg_block_time,
            'current_difficulty': self.blockchain.difficulty,
            'chain_valid': self.blockchain.is_chain_valid()
        }

    def calculate_wallet_metrics(self) -> Dict[str, Any]:
        """Calculate wallet-related metrics"""
        wallet_stats = defaultdict(lambda: {'sent': 0, 'received': 0, 'total_transactions': 0})
        
        for block in self.blockchain.chain:
            for tx in block.transactions:
                wallet_stats[tx.sender]['sent'] += tx.amount
                wallet_stats[tx.sender]['total_transactions'] += 1
                wallet_stats[tx.recipient]['received'] += tx.amount
                wallet_stats[tx.recipient]['total_transactions'] += 1

        # Find most active wallets
        most_active = sorted(
            wallet_stats.items(),
            key=lambda x: x[1]['total_transactions'],
            reverse=True
        )[:5]

        return {
            'wallet_stats': dict(wallet_stats),
            'most_active_wallets': most_active
        }

    def calculate_time_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Calculate time-based metrics"""
        now = datetime.utcnow()
        cutoff_timestamp = (now - timedelta(days=days)).timestamp()
        
        daily_transactions = defaultdict(int)
        daily_volume = defaultdict(float)
        
        for block in self.blockchain.chain:
            if block.timestamp >= cutoff_timestamp:
                day = datetime.fromtimestamp(block.timestamp).date()
                for tx in block.transactions:
                    daily_transactions[day] += 1
                    daily_volume[day] += tx.amount

        return {
            'daily_transactions': dict(daily_transactions),
            'daily_volume': dict(daily_volume)
        } 