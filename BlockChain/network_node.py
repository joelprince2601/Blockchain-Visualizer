from typing import List, Set, Dict, Optional
import socket
import json
import threading
from dataclasses import dataclass
from blockchain import Blockchain
from block import Block
from transaction import Transaction

@dataclass
class NodeInfo:
    address: str
    port: int
    is_mining: bool = False
    last_seen: float = 0

class BlockchainNode:
    def __init__(self, port: int, blockchain: Blockchain):
        self.port = port
        self.blockchain = blockchain
        self.peers: Dict[str, NodeInfo] = {}
        self.mining = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(5)

    def start(self):
        """Start the node's server and mining threads"""
        # Start server thread
        server_thread = threading.Thread(target=self._run_server)
        server_thread.daemon = True
        server_thread.start()

        # Start mining thread
        mining_thread = threading.Thread(target=self._mine_pending_transactions)
        mining_thread.daemon = True
        mining_thread.start()

    def _run_server(self):
        """Run the node's server to handle peer connections"""
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(
                target=self._handle_peer_connection,
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()

    def _handle_peer_connection(self, client_socket: socket.socket, address: tuple):
        """Handle incoming peer connections and messages"""
        try:
            data = client_socket.recv(4096).decode()
            message = json.loads(data)
            
            if message['type'] == 'new_block':
                self._handle_new_block(message['data'])
            elif message['type'] == 'new_transaction':
                self._handle_new_transaction(message['data'])
            elif message['type'] == 'chain_request':
                self._handle_chain_request(client_socket)
                
        except Exception as e:
            print(f"Error handling peer connection: {e}")
        finally:
            client_socket.close()

    def _handle_new_block(self, block_data: dict):
        """Handle receiving a new block from peers"""
        # Convert block data to Block object
        block = Block(
            index=block_data['index'],
            transactions=block_data['transactions'],
            previous_hash=block_data['previous_hash']
        )
        block.hash = block_data['hash']
        block.nonce = block_data['nonce']
        
        # Verify and add block
        if self.blockchain.verify_block(block):
            self.blockchain.add_block_from_peer(block)
            self._broadcast_block(block)

    def _handle_new_transaction(self, tx_data: dict):
        """Handle receiving a new transaction from peers"""
        transaction = Transaction(
            sender=tx_data['sender'],
            recipient=tx_data['recipient'],
            amount=tx_data['amount']
        )
        
        if self.blockchain.verify_transaction(transaction):
            self.blockchain.add_pending_transaction(transaction)
            self._broadcast_transaction(transaction)

    def _handle_chain_request(self, client_socket: socket.socket):
        """Handle request for full blockchain data"""
        chain_data = self.blockchain.to_dict()
        response = {
            'type': 'chain_response',
            'data': chain_data
        }
        client_socket.send(json.dumps(response).encode())

    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast a new transaction to all peers"""
        message = {
            'type': 'new_transaction',
            'data': transaction.to_dict()
        }
        self._broadcast_to_peers(message)

    def broadcast_block(self, block: Block):
        """Broadcast a new block to all peers"""
        message = {
            'type': 'new_block',
            'data': block.to_dict()
        }
        self._broadcast_to_peers(message)

    def _broadcast_to_peers(self, message: dict):
        """Send a message to all connected peers"""
        for peer_info in self.peers.values():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_info.address, peer_info.port))
                    s.send(json.dumps(message).encode())
            except Exception as e:
                print(f"Error broadcasting to peer: {e}")

    def _mine_pending_transactions(self):
        """Mine pending transactions in a loop"""
        while True:
            if self.mining and len(self.blockchain.pending_transactions) > 0:
                new_block = self.blockchain.mine_pending_transactions(
                    f"Node_{self.port}"
                )
                if new_block:
                    self.broadcast_block(new_block) 