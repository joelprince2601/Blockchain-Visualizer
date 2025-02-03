from flask import Flask, jsonify, request, render_template_string
from blockchain import Blockchain
from blockchain_db import BlockchainDB
from transaction import TransactionProcessor, Transaction
import time
from datetime import datetime

app = Flask(__name__)
db = BlockchainDB(":memory:")
blockchain = Blockchain(difficulty=4, db=db)
tx_processor = TransactionProcessor()

# Create some initial test transactions
def create_test_data():
    transactions = [
        ("Alice", "Bob", 50.0),
        ("Bob", "Charlie", 30.0),
        ("Charlie", "Alice", 20.0)
    ]
    
    for sender, recipient, amount in transactions:
        tx = tx_processor.create_transaction(sender, recipient, amount)
        blockchain.add_pending_transaction(tx)
    
    blockchain.mine_pending_transactions("miner_address")

# Updated HTML template with dark theme
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Blockchain Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {
            --bg-primary: #1a1b1e;
            --bg-secondary: #2c2d31;
            --text-primary: #e4e5e7;
            --text-secondary: #a1a2a5;
            --accent: #3498db;
            --success: #2ecc71;
            --border: #3f4044;
        }
        
        body { 
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }
        
        .container { 
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background-color: var(--bg-secondary);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background-color: var(--bg-secondary);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        
        .stat-card h3 {
            margin: 0;
            color: var(--text-secondary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: 600;
            margin: 10px 0;
            color: var(--accent);
        }
        
        .block {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            margin: 15px 0;
            padding: 20px;
            border-radius: 10px;
            transition: transform 0.2s;
        }
        
        .block:hover {
            transform: translateY(-2px);
        }
        
        .block h3 {
            margin: 0 0 15px 0;
            color: var(--accent);
        }
        
        .block-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .block-info p {
            margin: 5px 0;
            color: var(--text-secondary);
        }
        
        .block-info span {
            color: var(--text-primary);
            word-break: break-all;
        }
        
        .transaction {
            background-color: var(--bg-primary);
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            font-size: 0.9em;
            color: var(--text-secondary);
        }
        
        .transaction span {
            color: var(--success);
        }
        
        .balance-card {
            background-color: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
        }
        
        .balance-card .address {
            color: var(--text-primary);
            font-weight: 600;
        }
        
        .balance-card .amount {
            color: var(--success);
            font-weight: 600;
        }
        
        h2 {
            color: var(--text-primary);
            margin: 30px 0 20px 0;
            font-size: 1.5em;
        }
        
        .visualization-container {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
        }
        
        #blockchain-visualization {
            width: 100%;
            height: 600px;
            border: 1px solid var(--border);
            background-color: var(--bg-primary);
            margin: 20px 0;
        }
        
        .node-details {
            padding: 10px;
            background: rgba(0,0,0,0.8);
            border-radius: 5px;
            font-size: 12px;
            color: white;
        }
        
        .transaction-form {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: var(--text-secondary);
        }
        
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border);
            border-radius: 5px;
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }
        
        .submit-button {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .submit-button:hover {
            background-color: #2980b9;
        }
        
        .alert {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            display: none;
        }
        
        .alert-success {
            background-color: #2ecc71;
            color: white;
        }
        
        .alert-error {
            background-color: #e74c3c;
            color: white;
        }
        
        .address-legend {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
        }
        
        .legend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .legend-item {
            display: flex;
            align-items: start;
            padding: 15px;
            background-color: var(--bg-primary);
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        
        .legend-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            margin-right: 15px;
            flex-shrink: 0;
        }
        
        .legend-icon.system {
            background-color: #9b59b6;
            color: white;
        }
        
        .legend-icon.miner {
            background-color: #f1c40f;
            color: #34495e;
        }
        
        .legend-icon.user {
            background-color: #3498db;
            color: white;
        }
        
        .legend-details {
            flex-grow: 1;
        }
        
        .legend-details h4 {
            margin: 0 0 5px 0;
            color: var(--text-primary);
        }
        
        .legend-details p {
            margin: 0 0 8px 0;
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        .legend-details code {
            display: inline-block;
            padding: 3px 6px;
            background-color: var(--bg-secondary);
            border-radius: 4px;
            font-size: 0.85em;
            color: var(--accent);
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Blockchain Dashboard</h1>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Chain Length</h3>
                <div class="stat-value">{{ chain_status.length }}</div>
            </div>
            <div class="stat-card">
                <h3>Chain Status</h3>
                <div class="stat-value" style="color: {{ 'var(--success)' if chain_status.is_valid else 'red' }}">
                    {{ 'Valid' if chain_status.is_valid else 'Invalid' }}
                </div>
            </div>
            <div class="stat-card">
                <h3>Mining Difficulty</h3>
                <div class="stat-value">{{ chain_status.difficulty }}</div>
            </div>
        </div>

        <h2>Create New Transaction</h2>
        <div class="transaction-form">
            <div id="alert" class="alert"></div>
            <form id="transactionForm" onsubmit="return createTransaction(event)">
                <div class="form-group">
                    <label for="sender">Sender Address</label>
                    <input type="text" id="sender" name="sender" required>
                </div>
                <div class="form-group">
                    <label for="recipient">Recipient Address</label>
                    <input type="text" id="recipient" name="recipient" required>
                </div>
                <div class="form-group">
                    <label for="amount">Amount</label>
                    <input type="number" id="amount" name="amount" step="0.1" min="0.1" required>
                </div>
                <button type="submit" class="submit-button">Create Transaction</button>
            </form>
        </div>

        <h2>Blockchain Visualization</h2>
        <div id="blockchain-visualization"></div>

        <h2>Account Balances</h2>
        {% for address, balance in balances.items() %}
        <div class="balance-card">
            <span class="address">{{ address }}</span>
            <span class="amount">{{ balance }} coins</span>
        </div>
        {% endfor %}

        <h2>Blockchain</h2>
        {% for block in blocks %}
        <div class="block">
            <h3>Block #{{ block.block_index }}</h3>
            <div class="block-info">
                <p>Hash: <span>{{ block.hash }}</span></p>
                <p>Previous Hash: <span>{{ block.previous_hash }}</span></p>
                <p>Timestamp: <span>{{ block.timestamp }}</span></p>
                <p>Nonce: <span>{{ block.nonce }}</span></p>
            </div>
            <h4>Transactions:</h4>
            {% for tx in block.transactions %}
            <div class="transaction">
                <span>{{ tx.sender }}</span> → <span>{{ tx.recipient }}</span>: {{ tx.amount }} coins
            </div>
            {% endfor %}
        </div>
        {% endfor %}

        <h2>Address Legend</h2>
        <div class="address-legend">
            <div class="legend-grid">
                <div class="legend-item">
                    <div class="legend-icon system">SYS</div>
                    <div class="legend-details">
                        <h4>System Address</h4>
                        <p>Used for mining rewards and system operations</p>
                        <code>System</code>
                    </div>
                </div>
                <div class="legend-item">
                    <div class="legend-icon miner">MIN</div>
                    <div class="legend-details">
                        <h4>Miner Address</h4>
                        <p>Receives mining rewards</p>
                        <code>miner_address</code>
                    </div>
                </div>
                {% for address in known_addresses %}
                    {% if address not in ['System', 'miner_address'] %}
                        <div class="legend-item">
                            <div class="legend-icon user">USR</div>
                            <div class="legend-details">
                                <h4>User Address</h4>
                                <p>Balance: {{ balances[address] }} coins</p>
                                <code>{{ address }}</code>
                            </div>
                        </div>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
    </div>

    <script type="text/javascript">
        const container = document.getElementById('blockchain-visualization');
        const blocks = {{ blocks|tojson }};
        
        const nodes = [];
        const edges = [];
        let nodeId = 0;
        
        // Track block IDs for proper connections
        const blockIds = {};
        
        blocks.forEach(block => {
            // Add block node
            const blockId = nodeId++;
            blockIds[block.block_index] = blockId;
            
            // Add main block node
            nodes.push({
                id: blockId,
                label: `Block ${block.block_index}`,
                title: `<div class="node-details">
                    Hash: ${block.hash}<br>
                    Prev Hash: ${block.previous_hash}<br>
                    Nonce: ${block.nonce}<br>
                    Timestamp: ${new Date(block.timestamp * 1000).toLocaleString()}
                </div>`,
                shape: 'box',
                color: {
                    background: block.block_index === 0 ? '#2ecc71' : '#3498db',
                    border: '#2c3e50',
                    highlight: {
                        background: block.block_index === 0 ? '#27ae60' : '#2980b9',
                        border: '#34495e'
                    }
                },
                font: { color: '#fff', size: 14 },
                level: block.block_index * 2
            });

            // Add hash connection node
            const hashNodeId = nodeId++;
            nodes.push({
                id: hashNodeId,
                label: `Hash:\n${block.hash.substring(0, 8)}...`,
                title: `<div class="node-details">
                    Full Hash: ${block.hash}<br>
                    Previous Hash: ${block.previous_hash}
                </div>`,
                shape: 'hexagon',
                color: {
                    background: '#8e44ad',
                    border: '#6c3483',
                    highlight: {
                        background: '#9b59b6',
                        border: '#8e44ad'
                    }
                },
                font: { color: '#fff', size: 12 },
                size: 25,
                level: block.block_index * 2
            });

            // Connect block to its hash
            edges.push({
                from: blockId,
                to: hashNodeId,
                color: { color: '#8e44ad' },
                width: 2,
                arrows: {
                    to: {
                        enabled: true,
                        type: 'arrow'
                    }
                }
            });

            // Connect to previous block's hash
            if (block.block_index > 0) {
                edges.push({
                    from: hashNodeId,
                    to: blockIds[block.block_index - 1],
                    color: { color: '#8e44ad' },
                    width: 2,
                    arrows: {
                        to: {
                            enabled: true,
                            type: 'arrow'
                        }
                    },
                    dashes: true
                });
            }
            
            // Add transaction nodes
            block.transactions.forEach((tx, txIndex) => {
                const txNodeId = nodeId++;
                nodes.push({
                    id: txNodeId,
                    label: `${tx.sender}\n→\n${tx.recipient}\n${tx.amount} coins`,
                    title: `<div class="node-details">
                        From: ${tx.sender}<br>
                        To: ${tx.recipient}<br>
                        Amount: ${tx.amount} coins<br>
                        Time: ${new Date(tx.timestamp * 1000).toLocaleString()}
                    </div>`,
                    shape: 'diamond',
                    color: {
                        background: '#e74c3c',
                        border: '#c0392b',
                        highlight: {
                            background: '#c0392b',
                            border: '#a93226'
                        }
                    },
                    font: { color: '#fff', size: 12 },
                    size: 15,
                    level: block.block_index * 2 + 1
                });
                
                // Connect transaction to block
                edges.push({
                    from: blockId,
                    to: txNodeId,
                    color: { color: '#95a5a6' },
                    width: 1
                });
            });
        });

        const options = {
            nodes: {
                shape: 'box',
                margin: 10,
                widthConstraint: {
                    maximum: 200
                }
            },
            edges: {
                smooth: {
                    type: 'cubicBezier',
                    forceDirection: 'horizontal',
                    roundness: 0.4
                }
            },
            layout: {
                hierarchical: {
                    direction: 'LR',
                    sortMethod: 'directed',
                    levelSeparation: 250,
                    nodeSpacing: 150,
                    treeSpacing: 200
                }
            },
            physics: false,
            interaction: {
                hover: true,
                tooltipDelay: 0,
                zoomView: true
            }
        };

        const data = {
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges)
        };
        
        const network = new vis.Network(container, data, options);

        async function createTransaction(event) {
            event.preventDefault();
            
            const formData = new FormData(event.target);
            const alert = document.getElementById('alert');
            
            try {
                const response = await fetch('/create_transaction', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert.className = 'alert alert-success';
                    alert.textContent = result.message;
                    alert.style.display = 'block';
                    
                    // Refresh the page after 2 seconds to show the new transaction
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = result.message;
                    alert.style.display = 'block';
                }
            } catch (error) {
                alert.className = 'alert alert-error';
                alert.textContent = 'An error occurred while creating the transaction';
                alert.style.display = 'block';
            }
            
            return false;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Display a dashboard of the blockchain"""
    create_test_data()
    
    chain_status = {
        'length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(),
        'difficulty': blockchain.difficulty
    }
    
    blocks = []
    for block in blockchain.chain:
        block_dict = {
            'block_index': block.index,
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'timestamp': block.timestamp,
            'transactions': [{
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            } for tx in block.transactions]
        }
        blocks.append(block_dict)
    
    # Get all unique addresses from transactions
    addresses = set(["Alice", "Bob", "Charlie", "miner_address", "System"])
    for block in blockchain.chain:
        for tx in block.transactions:
            addresses.add(tx.sender)
            addresses.add(tx.recipient)
    
    # Calculate balances for all known addresses
    balances = {
        address: tx_processor.get_balance(address, blockchain)
        for address in addresses
    }
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        chain_status=chain_status,
        blocks=blocks,
        balances=balances,
        known_addresses=sorted(addresses),
        datetime=datetime
    )

# Keep the existing API endpoints
@app.route('/blocks', methods=['GET'])
def get_blocks():
    blocks = db.get_all_blocks()
    return jsonify(blocks)

@app.route('/blocks/<int:index>', methods=['GET'])
def get_block(index):
    block = db.get_block(index)
    if block:
        return jsonify(block)
    return jsonify({'error': 'Block not found'}), 404

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = tx_processor.get_balance(address, blockchain)
    return jsonify({'address': address, 'balance': balance})

@app.route('/chain/status', methods=['GET'])
def get_chain_status():
    return jsonify({
        'length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(),
        'difficulty': blockchain.difficulty
    })

# Add this route to handle new transactions
@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    try:
        sender = request.form['sender']
        recipient = request.form['recipient']
        amount = float(request.form['amount'])
        
        tx = tx_processor.create_transaction(sender, recipient, amount)
        blockchain.add_pending_transaction(tx)
        blockchain.mine_pending_transactions("miner_address")
        
        return jsonify({'success': True, 'message': 'Transaction created and mined successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 