#!/usr/bin/env python3
"""
BlackRock BUIDL Holder Analysis
Analyze on-chain behavior of BUIDL token holders
"""

import requests
import json
import time
from collections import defaultdict
from datetime import datetime
import pandas as pd

# Configuration
BUIDL_CONTRACT = "0x7712c34205737192402172409a8f7ccef8aa2aec"
ETHERSCAN_API_KEY = "EH2EBW54AHN4JC1DR5ZC12GDKFG554JX7D"
ETHERSCAN_BASE = "https://api.etherscan.io/api"

# Known DeFi protocols
DEFI_PROTOCOLS = {
    "morpho": ["0x", "morpho"],  # Will update with actual addresses
    "aave": ["0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9"],
    "compound": ["0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b"],
}

# Competitor RWA tokens
COMPETITOR_TOKENS = {
    "USDY": "0x96F6eF951840721AdBF46Ac996b59E0235CB985C",  # Ondo USDY
    "OUSG": "0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92",  # Ondo OUSG
    "BENJI": "0x", # Franklin Templeton BENJI - need to find contract
}

# Bridge contracts (major ones)
BRIDGE_CONTRACTS = [
    "0x", # Stargate
    "0x", # LayerZero
    "0x", # Wormhole
]

def get_token_holders(contract_address, api_key):
    """Get list of token holders from Etherscan"""
    print(f"Fetching holders for {contract_address}...")
    
    # Try to get holders via token balance endpoint
    # Note: Etherscan doesn't have a direct "get all holders" endpoint
    # We'll need to use token transfer events
    
    url = f"{ETHERSCAN_BASE}"
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": contract_address,
        "page": 1,
        "offset": 10000,
        "sort": "desc",
        "apikey": api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["status"] != "1":
        print(f"Error: {data.get('message', 'Unknown error')}")
        return []
    
    # Extract unique holder addresses from transfers
    holders = set()
    for tx in data["result"]:
        # Add 'to' addresses (receivers)
        holders.add(tx["to"].lower())
    
    # Now get current balances for each holder
    holder_balances = {}
    for holder in holders:
        balance = get_token_balance(holder, contract_address, api_key)
        if balance > 0:
            holder_balances[holder] = balance
        time.sleep(0.2)  # Rate limiting
    
    print(f"Found {len(holder_balances)} holders with non-zero balances")
    return holder_balances

def get_token_balance(address, token_contract, api_key):
    """Get ERC20 token balance for an address"""
    url = f"{ETHERSCAN_BASE}"
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": token_contract,
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "1":
            return int(data["result"]) / 10**6  # BUIDL has 6 decimals
        return 0
    except Exception as e:
        print(f"Error getting balance for {address}: {e}")
        return 0

def get_address_transactions(address, api_key):
    """Get all transactions for an address"""
    url = f"{ETHERSCAN_BASE}"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "1":
            return data["result"]
        return []
    except Exception as e:
        print(f"Error getting transactions for {address}: {e}")
        return []

def get_erc20_transfers(address, api_key):
    """Get ERC20 token transfers for an address"""
    url = f"{ETHERSCAN_BASE}"
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "1":
            return data["result"]
        return []
    except Exception as e:
        print(f"Error getting token transfers for {address}: {e}")
        return []

def classify_holder_behavior(address, buidl_balance, api_key):
    """
    Classify holder behavior into 5 categories:
    1. Pure Holder - BUIDL never left, low interaction
    2. DeFi Active - Deposited into lending protocols
    3. Trading - Frequent mint/redeem cycles
    4. Cross-chain - Bridged to other chains
    5. Competitor Cross-holder - Also holds USDY/OUSG/BENJI
    """
    print(f"Analyzing {address}...")
    
    # Get transaction history
    txs = get_address_transactions(address, api_key)
    token_transfers = get_erc20_transfers(address, api_key)
    
    time.sleep(0.2)  # Rate limiting
    
    # Filter BUIDL transfers
    buidl_transfers = [
        tx for tx in token_transfers 
        if tx["contractAddress"].lower() == BUIDL_CONTRACT.lower()
    ]
    
    # Calculate metrics
    metrics = {
        "address": address,
        "buidl_balance": buidl_balance,
        "total_txs": len(txs),
        "buidl_transfers_out": len([tx for tx in buidl_transfers if tx["from"].lower() == address.lower()]),
        "buidl_transfers_in": len([tx for tx in buidl_transfers if tx["to"].lower() == address.lower()]),
        "first_buidl_tx": None,
        "last_buidl_tx": None,
        "interacted_with_defi": False,
        "interacted_with_bridges": False,
        "holds_competitors": False,
        "unique_counterparties": set(),
    }
    
    # Analyze BUIDL transfers
    if buidl_transfers:
        timestamps = [int(tx["timeStamp"]) for tx in buidl_transfers]
        metrics["first_buidl_tx"] = min(timestamps)
        metrics["last_buidl_tx"] = max(timestamps)
        
        # Track counterparties
        for tx in buidl_transfers:
            if tx["from"].lower() == address.lower():
                metrics["unique_counterparties"].add(tx["to"].lower())
            else:
                metrics["unique_counterparties"].add(tx["from"].lower())
    
    # Check for DeFi interactions
    for tx in txs:
        to_address = tx.get("to", "").lower()
        # Check against known DeFi protocols
        for protocol, addresses in DEFI_PROTOCOLS.items():
            if any(addr.lower() in to_address for addr in addresses):
                metrics["interacted_with_defi"] = True
                break
    
    # Check for bridge interactions
    for tx in txs:
        to_address = tx.get("to", "").lower()
        if any(bridge.lower() in to_address for bridge in BRIDGE_CONTRACTS if bridge):
            metrics["interacted_with_bridges"] = True
            break
    
    # Check for competitor token holdings
    for token_name, token_address in COMPETITOR_TOKENS.items():
        if not token_address or token_address == "0x":
            continue
        balance = get_token_balance(address, token_address, api_key)
        if balance > 0:
            metrics["holds_competitors"] = True
            metrics[f"{token_name}_balance"] = balance
        time.sleep(0.2)
    
    # Classification logic
    category = classify_from_metrics(metrics)
    metrics["category"] = category
    metrics["unique_counterparties"] = len(metrics["unique_counterparties"])
    
    return metrics

def classify_from_metrics(metrics):
    """Determine category based on metrics"""
    
    # Category 5: Competitor Cross-holder
    if metrics["holds_competitors"]:
        return "Competitor Cross-holder"
    
    # Category 4: Cross-chain
    if metrics["interacted_with_bridges"]:
        return "Cross-chain"
    
    # Category 2: DeFi Active
    if metrics["interacted_with_defi"]:
        return "DeFi Active"
    
    # Category 3: Trading (frequent transfers)
    if metrics["buidl_transfers_out"] >= 5:
        return "Trading"
    
    # Category 1: Pure Holder (default)
    if metrics["buidl_transfers_out"] <= 1 and metrics["total_txs"] < 10:
        return "Pure Holder"
    
    # If moved BUIDL but not frequently
    if metrics["buidl_transfers_out"] > 1:
        return "Moderate Activity"
    
    return "Pure Holder"

def main():
    print("=" * 80)
    print("BlackRock BUIDL Holder Analysis")
    print("=" * 80)
    print()
    
    # Step 1: Get holders
    print("Step 1: Fetching BUIDL holders...")
    holders = get_token_holders(BUIDL_CONTRACT, ETHERSCAN_API_KEY)
    
    if not holders:
        print("ERROR: Could not fetch holders. Trying alternative method...")
        # Alternative: Use a known list or Dune Analytics
        print("Please check if we need to use Dune Analytics API instead")
        return
    
    print(f"Found {len(holders)} holders")
    print()
    
    # Step 2: Analyze each holder
    print("Step 2: Analyzing holder behaviors...")
    results = []
    
    for i, (address, balance) in enumerate(holders.items(), 1):
        print(f"[{i}/{len(holders)}] Analyzing {address[:10]}...")
        try:
            analysis = classify_holder_behavior(address, balance, ETHERSCAN_API_KEY)
            results.append(analysis)
        except Exception as e:
            print(f"Error analyzing {address}: {e}")
        
        # Save checkpoint every 10 addresses
        if i % 10 == 0:
            df = pd.DataFrame(results)
            df.to_csv("checkpoint.csv", index=False)
            print(f"Checkpoint saved ({i} addresses analyzed)")
    
    # Step 3: Save results
    print()
    print("Step 3: Saving results...")
    df = pd.DataFrame(results)
    df.to_csv("holder_analysis.csv", index=False)
    df.to_json("holder_analysis.json", orient="records", indent=2)
    
    print(f"Analysis complete! Results saved to holder_analysis.csv")
    print()
    
    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    category_counts = df["category"].value_counts()
    print("\nHolder Distribution by Category:")
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {category}: {count} holders ({percentage:.1f}%)")
    
    print(f"\nTotal BUIDL analyzed: ${df['buidl_balance'].sum():,.2f}")
    print("\nCategory breakdown by value:")
    for category in category_counts.index:
        cat_value = df[df["category"] == category]["buidl_balance"].sum()
        percentage = (cat_value / df["buidl_balance"].sum()) * 100
        print(f"  {category}: ${cat_value:,.2f} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
