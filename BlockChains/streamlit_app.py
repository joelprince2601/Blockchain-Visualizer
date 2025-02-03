import os
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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Blockchain Visualizer",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize components with error handling
@st.cache_resource
def init_blockchain():
    try:
        db = BlockchainDB()
        blockchain = Blockchain(
            difficulty=int(os.getenv('BLOCKCHAIN_DIFFICULTY', '4')),
            db=db
        )
        tx_processor = TransactionProcessor()
        return db, blockchain, tx_processor
    except Exception as e:
        st.error(f"Failed to initialize blockchain: {str(e)}")
        return None, None, None

# Initialize with error handling
db, blockchain, tx_processor = init_blockchain()

if None in (db, blockchain, tx_processor):
    st.error("Application failed to initialize properly. Please check your configuration.")
    st.stop()

# Set up the Streamlit page
st.title("Blockchain Visualizer")

# Sidebar controls
st.sidebar.header("Controls")

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

# Enhanced transaction creation form
st.sidebar.header("Create Transaction")
with st.sidebar.form("transaction_form", clear_on_submit=True):
    sender = st.text_input("Sender Address", help="Enter the sender's wallet address")
    recipient = st.text_input("Recipient Address", help="Enter the recipient's wallet address")
    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=0.0,
        step=0.1,
        help="Enter the amount to transfer"
    )
    
    if st.form_submit_button("Create Transaction", use_container_width=True):
        try:
            if not sender or not recipient:
                st.error("Please provide both sender and recipient addresses")
            elif amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                with st.spinner("Processing transaction..."):
                    tx = tx_processor.create_transaction(sender, recipient, amount)
                    blockchain.add_pending_transaction(tx)
                    blockchain.mine_pending_transactions("miner_address")
                st.success("Transaction created and mined successfully!")
                time.sleep(2)
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error creating transaction: {str(e)}")

# Add session state for refresh control
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Auto-refresh control
refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    min_value=5,
    max_value=60,
    value=30,
    help="Select how often the dashboard should refresh"
)

# Manual refresh button
if st.sidebar.button("Refresh Data", use_container_width=True):
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# Automatic refresh using time-based check
if time.time() - st.session_state.last_refresh > refresh_interval:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# Footer
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Blockchain Visualizer v1.0</p>
        <p>Built with Streamlit 🎈</p>
    </div>
""", unsafe_allow_html=True) 