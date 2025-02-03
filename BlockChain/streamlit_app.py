import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
from blockchain import Blockchain
from blockchain_db import BlockchainDB
from transaction import TransactionProcessor
import networkx as nx

# Initialize components
@st.cache_resource
def init_blockchain():
    db = BlockchainDB()
    blockchain = Blockchain(difficulty=4, db=db)
    tx_processor = TransactionProcessor()
    return db, blockchain, tx_processor

db, blockchain, tx_processor = init_blockchain()

# Set up the Streamlit page
st.set_page_config(page_title="Blockchain Visualizer", layout="wide")
st.title("Blockchain Visualizer")

# Sidebar controls
st.sidebar.header("Controls")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 30)

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Blockchain Metrics", "Block Explorer", "Transaction Flow"])

with tab1:
    # Basic Metrics Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Blocks", len(blockchain.chain))
    
    with col2:
        total_transactions = sum(len(block.transactions) for block in blockchain.chain)
        st.metric("Total Transactions", total_transactions)
    
    with col3:
        st.metric("Current Difficulty", blockchain.difficulty)

    # Transaction Volume Chart
    st.subheader("Transaction Volume Over Time")
    
    # Prepare data for the chart
    volume_data = []
    for block in blockchain.chain:
        volume_data.append({
            'timestamp': datetime.fromtimestamp(block.timestamp),
            'transactions': len(block.transactions)
        })
    
    if volume_data:
        df = pd.DataFrame(volume_data)
        fig = px.line(df, x='timestamp', y='transactions', 
                     title='Transaction Volume Over Time')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Block Explorer
    st.subheader("Block Explorer")
    
    # Block selection
    selected_block_index = st.selectbox(
        "Select Block",
        range(len(blockchain.chain)),
        format_func=lambda x: f"Block #{x}"
    )
    
    # Display block details
    if selected_block_index is not None:
        block = blockchain.chain[selected_block_index]
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Block Details")
            st.json({
                'index': block.index,
                'timestamp': datetime.fromtimestamp(block.timestamp).isoformat(),
                'previous_hash': block.previous_hash,
                'hash': block.hash,
                'nonce': block.nonce
            })
        
        with col2:
            st.write("Transactions")
            for tx in block.transactions:
                st.write(f"From: {tx.sender}")
                st.write(f"To: {tx.recipient}")
                st.write(f"Amount: {tx.amount}")
                st.write("---")

with tab3:
    # Transaction Flow Visualization
    st.subheader("Transaction Flow Network")
    
    # Create network graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    wallets = set()
    transactions = []
    
    for block in blockchain.chain:
        for tx in block.transactions:
            wallets.add(tx.sender)
            wallets.add(tx.recipient)
            transactions.append((tx.sender, tx.recipient, tx.amount))
    
    # Add nodes
    for wallet in wallets:
        G.add_node(wallet)
    
    # Add edges
    for sender, recipient, amount in transactions:
        G.add_edge(sender, recipient, weight=amount)
    
    # Create Plotly figure
    pos = nx.spring_layout(G)
    
    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=0.5, color='#888'),
        hoverinfo='none', mode='lines')
    
    node_trace = go.Scatter(
        x=[], y=[], mode='markers+text',
        hoverinfo='text', marker=dict(size=20))
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)
    
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace.x = node_x
    node_trace.y = node_y
    node_trace.text = node_text
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0,l=0,r=0,t=0),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                   ))
    
    st.plotly_chart(fig, use_container_width=True)

# Add transaction creation form
st.sidebar.header("Create Transaction")
with st.sidebar.form("transaction_form"):
    sender = st.text_input("Sender Address")
    recipient = st.text_input("Recipient Address")
    amount = st.number_input("Amount", min_value=0.0, value=0.0)
    
    if st.form_submit_button("Create Transaction"):
        try:
            tx = tx_processor.create_transaction(sender, recipient, amount)
            blockchain.add_pending_transaction(tx)
            blockchain.mine_pending_transactions("miner_address")
            st.success("Transaction created and mined successfully!")
        except Exception as e:
            st.error(f"Error creating transaction: {str(e)}")

# Auto-refresh
if st.sidebar.button("Refresh Data"):
    st.experimental_rerun()

# Add auto-refresh using JavaScript
st.markdown(
    f"""
    <script>
        var timer = setTimeout(function() {{
            window.location.reload();
        }}, {refresh_interval * 1000});
    </script>
    """,
    unsafe_allow_html=True
) 
