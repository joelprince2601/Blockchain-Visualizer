from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    timestamp: datetime = datetime.utcnow()
    signature: Optional[str] = None

    def to_dict(self):
        """Convert transaction to dictionary format"""
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': str(self.timestamp),
            'signature': self.signature
        }

class TransactionProcessor:
    def __init__(self):
        self.pending_transactions = []

    def create_transaction(self, sender: str, recipient: str, amount: float) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(sender, recipient, amount)
        self.pending_transactions.append(transaction)
        return transaction

    def validate_transaction(self, transaction: Transaction) -> bool:
        """
        Validate a single transaction
        Basic validation - can be extended with more complex rules
        """
        if transaction.amount <= 0:
            return False
        if transaction.sender == transaction.recipient:
            return False
        # Add more validation rules as needed
        return True

    def get_balance(self, address: str, blockchain) -> float:
        """Calculate the balance of an address by looking through all blockchain transactions"""
        balance = 0.0
        
        for block in blockchain.chain:
            for transaction in block.transactions:
                # Handle both dictionary and Transaction object formats
                if isinstance(transaction, dict):
                    if transaction['recipient'] == address:
                        balance += transaction['amount']
                    if transaction['sender'] == address:
                        balance -= transaction['amount']
                else:
                    if transaction.recipient == address:
                        balance += transaction.amount
                    if transaction.sender == address:
                        balance -= transaction.amount
                    
        return balance 