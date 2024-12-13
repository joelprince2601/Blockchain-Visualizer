import sqlite3
from typing import List, Optional
from block import Block
from transaction import Transaction
from datetime import datetime

class BlockchainDB:
    def __init__(self, db_file: str = "blockchain.db"):
        self.db_file = db_file
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables"""
        # For in-memory database, we need to maintain the connection
        if self.db_file == ":memory:":
            self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
            self._create_tables(self.connection)
        else:
            with sqlite3.connect(self.db_file) as conn:
                self._create_tables(conn)

    def _create_tables(self, conn) -> None:
        """Create the database tables"""
        cursor = conn.cursor()

        # Create blocks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            block_index INTEGER PRIMARY KEY,
            timestamp REAL,
            previous_hash TEXT,
            hash TEXT,
            nonce INTEGER
        )
        ''')

        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER,
            sender TEXT,
            recipient TEXT,
            amount REAL,
            timestamp REAL,
            FOREIGN KEY (block_index) REFERENCES blocks (block_index)
        )
        ''')

        conn.commit()

    def _get_connection(self):
        """Get a database connection"""
        if self.db_file == ":memory:":
            return self.connection
        return sqlite3.connect(self.db_file)

    def save_block(self, block: Block) -> None:
        """Save a block and its transactions to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Save block
            cursor.execute('''
            INSERT INTO blocks (block_index, timestamp, previous_hash, hash, nonce)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                block.index,
                block.timestamp,
                block.previous_hash,
                block.hash,
                block.nonce
            ))

            # Save transactions
            for tx in block.transactions:
                cursor.execute('''
                INSERT INTO transactions (block_index, sender, recipient, amount, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    block.index,
                    tx.sender,
                    tx.recipient,
                    tx.amount,
                    tx.timestamp
                ))

            conn.commit()
        except Exception as e:
            print(f"Error saving block: {e}")
            conn.rollback()
        finally:
            if self.db_file != ":memory:":
                conn.close()

    def get_block(self, index: int) -> Optional[dict]:
        """Retrieve a block and its transactions by index"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get block
            cursor.execute('SELECT * FROM blocks WHERE block_index = ?', (index,))
            block_data = cursor.fetchone()
            
            if not block_data:
                return None

            # Get transactions for this block
            cursor.execute('SELECT * FROM transactions WHERE block_index = ?', (index,))
            transactions = cursor.fetchall()

            # Convert transactions to Transaction objects
            transaction_objects = [
                Transaction(
                    sender=tx[2],
                    recipient=tx[3],
                    amount=tx[4],
                    timestamp=tx[5]
                ) for tx in transactions
            ]

            return {
                'block_index': block_data[0],
                'timestamp': block_data[1],
                'previous_hash': block_data[2],
                'hash': block_data[3],
                'nonce': block_data[4],
                'transactions': transaction_objects
            }
        finally:
            if self.db_file != ":memory:":
                conn.close()

    def get_all_blocks(self) -> List[dict]:
        """Retrieve all blocks with their transactions"""
        blocks = []
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT block_index FROM blocks ORDER BY block_index')
            block_indices = cursor.fetchall()

            for (index,) in block_indices:
                block = self.get_block(index)
                if block:
                    blocks.append(block)

            return blocks
        finally:
            if self.db_file != ":memory:":
                conn.close() 