from typing import Dict, List, Any
from datetime import datetime
from blockchain import Blockchain
from blockchain_db import BlockchainDB

class BlockchainFormatter:
    def __init__(self, blockchain: Blockchain, db: BlockchainDB):
        self.blockchain = blockchain
        self.db = db

    def format_for_graph(self, page: int = 1, page_size: int = 20) -> Dict[str, List[Any]]:
        """Format blockchain data for graph visualization with pagination"""
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get subset of chain
        chain_subset = self.blockchain.chain[start_idx:end_idx]
        
        nodes = []
        edges = []
        
        # Create nodes for blocks
        for block in chain_subset:
            nodes.append({
                'id': f'block_{block.index}',
                'label': f'Block {block.index}',
                'type': 'block',
                'hash': block.hash[:8],  # First 8 chars of hash
                'timestamp': datetime.fromtimestamp(block.timestamp).isoformat(),
                'size': len(block.transactions)
            })
            
            # Add edge to previous block
            if block.index > 0:
                edges.append({
                    'from': f'block_{block.index - 1}',
                    'to': f'block_{block.index}',
                    'type': 'blockchain'
                })

            # Add nodes and edges for transactions
            for tx in block.transactions:
                tx_id = f'tx_{block.index}_{tx.timestamp.isoformat()}'
                nodes.append({
                    'id': tx_id,
                    'label': f'{tx.amount} coins',
                    'type': 'transaction',
                    'sender': tx.sender,
                    'recipient': tx.recipient,
                    'amount': tx.amount
                })
                
                edges.append({
                    'from': tx_id,
                    'to': f'block_{block.index}',
                    'type': 'contains'
                })

        return {
            'nodes': nodes,
            'edges': edges,
            'total_pages': (len(self.blockchain.chain) + page_size - 1) // page_size,
            'current_page': page
        }

    def format_transaction_flow(self) -> Dict[str, List[Any]]:
        """Format transaction flow between wallets"""
        nodes = []
        edges = []
        wallets = set()
        
        # Collect all wallet addresses
        for block in self.blockchain.chain:
            for tx in block.transactions:
                wallets.add(tx.sender)
                wallets.add(tx.recipient)
        
        # Create nodes for wallets
        for wallet in wallets:
            nodes.append({
                'id': wallet,
                'label': wallet,
                'type': 'wallet'
            })
        
        # Create edges for transactions
        for block in self.blockchain.chain:
            for tx in block.transactions:
                edges.append({
                    'from': tx.sender,
                    'to': tx.recipient,
                    'value': tx.amount,
                    'title': f'{tx.amount} coins'
                })
        
        return {
            'nodes': nodes,
            'edges': edges
        } 