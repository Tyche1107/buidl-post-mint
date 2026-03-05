#!/usr/bin/env python3
"""
Fetch REAL BlackRock BUIDL holder data from Etherscan API
NO simulated data - only real on-chain facts
"""

import requests
import json
import time
import os
from datetime import datetime

# BUIDL contract on Ethereum
BUIDL_CONTRACT = "0x7712c34205737192402172409a8F7ccef8aA2AEc"
ONDO_USDY_CONTRACT = "0x96F6eF951840721AdBF46Ac996b59E0235CB985C"
ONDO_OUSG_CONTRACT = "0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92"

# Get Etherscan API keys from credentials
CREDENTIALS_PATH = os.path.expanduser("~/clawd/credentials/all-credentials.md")
API_KEYS = []

# Parse credentials file - format: "- Key N: `KEYSTRING`"
with open(CREDENTIALS_PATH) as f:
    for line in f:
        if "Key " in line and "`" in line and "Etherscan" not in line:
            # Extract key from backticks
            parts = line.split("`")
            if len(parts) >= 2:
                key = parts[1].strip()
                if key and len(key) > 20:
                    API_KEYS.append(key)

print(f"✅ Loaded {len(API_KEYS)} Etherscan API keys")

current_key_idx = 0

def get_next_api_key():
    """Rotate through API keys to avoid rate limits"""
    global current_key_idx
    key = API_KEYS[current_key_idx]
    current_key_idx = (current_key_idx + 1) % len(API_KEYS)
    return key

def fetch_token_holders(contract_address, token_name):
    """
    Fetch all holder addresses for a token
    Uses tokensupply endpoint to get total supply, then tokentx to get all transfers
    """
    print(f"\n🔍 Fetching holders for {token_name} ({contract_address})...")
    
    api_key = get_next_api_key()
    
    # Get all Transfer events (V2 endpoint required)
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": "1",
        "module": "account",
        "action": "tokentx",
        "contractaddress": contract_address,
        "page": 1,
        "offset": 10000,  # Max per request
        "sort": "asc",
        "apikey": api_key
    }
    
    all_transfers = []
    page = 1
    
    while True:
        params["page"] = page
        print(f"  📄 Fetching page {page}...")
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] != "1":
            print(f"  ⚠️ API error: {data.get('message', 'Unknown')}")
            break
        
        transfers = data["result"]
        if not transfers or len(transfers) == 0:
            break
        
        all_transfers.extend(transfers)
        print(f"  ✅ Got {len(transfers)} transfers (total: {len(all_transfers)})")
        
        if len(transfers) < 10000:
            break
        
        page += 1
        time.sleep(0.2)  # Rate limit protection
    
    # Calculate current balances
    balances = {}
    for tx in all_transfers:
        from_addr = tx["from"].lower()
        to_addr = tx["to"].lower()
        value = int(tx["value"])
        
        if from_addr != "0x0000000000000000000000000000000000000000":
            balances[from_addr] = balances.get(from_addr, 0) - value
        
        if to_addr != "0x0000000000000000000000000000000000000000":
            balances[to_addr] = balances.get(to_addr, 0) + value
    
    # Filter to holders with balance > 0
    holders = {addr: bal for addr, bal in balances.items() if bal > 0}
    
    print(f"✅ {token_name}: Found {len(holders)} holders with {len(all_transfers)} total transfers")
    
    return {
        "token": token_name,
        "contract": contract_address,
        "holder_count": len(holders),
        "transfer_count": len(all_transfers),
        "holders": holders,
        "all_transfers": all_transfers
    }

def check_defi_integration(holder_address):
    """
    Check if an address has interacted with major DeFi protocols
    Returns dict of protocol interactions
    """
    # Known DeFi protocol contracts
    DEFI_PROTOCOLS = {
        "Aave V3": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        "Morpho": "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb",
        "Compound V3": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
        "Spark": "0xC13e21B648A5Ee794902342038FF3aDAB66BE987",
    }
    
    api_key = get_next_api_key()
    interactions = {}
    
    for protocol_name, protocol_addr in DEFI_PROTOCOLS.items():
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": "1",
            "module": "account",
            "action": "txlist",
            "address": holder_address,
            "page": 1,
            "offset": 10,  # Just check if ANY interaction exists
            "sort": "desc",
            "apikey": api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "1" and data["result"]:
            # Check if any tx interacted with this protocol
            has_interaction = any(
                tx.get("to", "").lower() == protocol_addr.lower() 
                for tx in data["result"]
            )
            if has_interaction:
                interactions[protocol_name] = True
        
        time.sleep(0.15)  # Rate limit
    
    return interactions

def main():
    """Main execution"""
    print("=" * 60)
    print("BlackRock BUIDL Real Data Fetcher")
    print("=" * 60)
    
    # Fetch BUIDL holders
    buidl_data = fetch_token_holders(BUIDL_CONTRACT, "BUIDL")
    
    # Fetch Ondo USDY holders for comparison
    ondo_usdy_data = fetch_token_holders(ONDO_USDY_CONTRACT, "USDY")
    
    # Fetch Ondo OUSG holders
    ondo_ousg_data = fetch_token_holders(ONDO_OUSG_CONTRACT, "OUSG")
    
    # Save raw data
    output_data = {
        "fetch_date": datetime.now().isoformat(),
        "buidl": buidl_data,
        "ondo_usdy": ondo_usdy_data,
        "ondo_ousg": ondo_ousg_data,
    }
    
    with open("data/raw_holder_data.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"BUIDL holders: {buidl_data['holder_count']:,}")
    print(f"USDY holders: {ondo_usdy_data['holder_count']:,}")
    print(f"OUSG holders: {ondo_ousg_data['holder_count']:,}")
    print(f"\n✅ Data saved to data/raw_holder_data.json")
    
    # Check for overlapping holders
    buidl_holders = set(buidl_data['holders'].keys())
    usdy_holders = set(ondo_usdy_data['holders'].keys())
    ousg_holders = set(ondo_ousg_data['holders'].keys())
    
    overlap_usdy = buidl_holders & usdy_holders
    overlap_ousg = buidl_holders & ousg_holders
    
    print(f"\n🔍 Cross-holding analysis:")
    print(f"  BUIDL + USDY overlap: {len(overlap_usdy)} addresses")
    print(f"  BUIDL + OUSG overlap: {len(overlap_ousg)} addresses")
    
    # Sample DeFi check (first 5 BUIDL holders)
    print(f"\n🔍 Checking DeFi integration (sample)...")
    sample_holders = list(buidl_data['holders'].keys())[:5]
    
    for addr in sample_holders:
        defi = check_defi_integration(addr)
        if defi:
            print(f"  {addr[:10]}... → {', '.join(defi.keys())}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    main()
