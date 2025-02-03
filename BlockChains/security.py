from typing import List, Optional
import hashlib
from datetime import datetime
from block import Block
from transaction import Transaction

class BlockchainSecurity:
    @staticmethod
    def verify_block_integrity(block: Block) -> bool:
        """Verify the integrity of a single block"""
        # Verify block hash
        calculated_hash = block.calculate_hash()
        if calculated_hash != block.hash:
            return False
            
        # Verify proof of work
        if not block.hash.startswith('0' * block.difficulty):
            return False
            
        # Verify transaction signatures
        for tx in block.transactions:
            if not BlockchainSecurity.verify_transaction_signature(tx):
                return False
                
        return True

    @staticmethod
    def verify_chain_integrity(chain: List[Block]) -> bool:
        """Verify the integrity of the entire blockchain"""
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]
            
            # Verify block linkage
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # Verify current block
            if not BlockchainSecurity.verify_block_integrity(current_block):
                return False
                
        return True

    @staticmethod
    def verify_transaction_signature(transaction: Transaction) -> bool:
        """Verify the signature of a transaction"""
        if not transaction.signature:
            return False
            
        try:
            # Implement signature verification logic here
            # This is a placeholder for actual cryptographic verification
            message = f"{transaction.sender}{transaction.recipient}{transaction.amount}"
            return True  # Replace with actual verification
        except Exception:
            return False

    @staticmethod
    def detect_double_spending(chain: List[Block], transaction: Transaction) -> bool:
        """Detect if a transaction is attempting double spending"""
        sender_balance = 0
        spent_amount = 0
        
        # Calculate sender's balance and spent amount
        for block in chain:
            for tx in block.transactions:
                if tx.recipient == transaction.sender:
                    sender_balance += tx.amount
                if tx.sender == transaction.sender:
                    spent_amount += tx.amount
                    
        # Check if sender has enough balance
        return (sender_balance - spent_amount) >= transaction.amount

    @staticmethod
    def audit_chain(chain: List[Block]) -> List[dict]:
        """Perform a security audit of the blockchain"""
        audit_results = []
        
        for i, block in enumerate(chain):
            block_audit = {
                'block_index': block.index,
                'timestamp': block.timestamp,
                'issues': []
            }
            
            # Check block integrity
            if not BlockchainSecurity.verify_block_integrity(block):
                block_audit['issues'].append('Block integrity compromised')
                
            # Check block linkage
            if i > 0 and block.previous_hash != chain[i-1].hash:
                block_audit['issues'].append('Invalid block linkage')
                
            # Check transactions
            for tx in block.transactions:
                if not BlockchainSecurity.verify_transaction_signature(tx):
                    block_audit['issues'].append(
                        f'Invalid transaction signature: {tx.sender} -> {tx.recipient}'
                    )
                    
            if block_audit['issues']:
                audit_results.append(block_audit)
                
        return audit_results 