#!/usr/bin/env python3
"""
Get BUIDL holders from Etherscan
Using multiple approaches for reliability
"""

import requests
import json
import time
from web3 import Web3

BUIDL_CONTRACT = "0x7712c34205737192402172409a8f7ccef8aa2aec"
ETHERSCAN_API_KEY = "EH2EBW54AHN4JC1DR5ZC12GDKFG554JX7D"
ETHERSCAN_BASE = "https://api.etherscan.io/api"

# ERC20 ABI for balanceOf
ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')

def get_holders_from_transfers():
    """
    Get unique holders by analyzing all Transfer events
    This is comprehensive but requires multiple API calls
    """
    print("Fetching all BUIDL transfer events...")
    
    all_transfers = []
    page = 1
    
    while True:
        url = f"{ETHERSCAN_BASE}"
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": BUIDL_CONTRACT,
            "page": page,
            "offset": 10000,  # Max per page
            "sort": "asc",
            "apikey": ETHERSCAN_API_KEY
        }
        
        print(f"Fetching page {page}...")
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] != "1":
            if "No transactions found" in data.get("message", ""):
                break
            print(f"Error: {data.get('message', 'Unknown error')}")
            break
        
        transfers = data["result"]
        if not transfers:
            break
            
        all_transfers.extend(transfers)
        print(f"  Fetched {len(transfers)} transfers (total: {len(all_transfers)})")
        
        if len(transfers) < 10000:  # Last page
            break
            
        page += 1
        time.sleep(0.2)  # Rate limiting
    
    print(f"\nTotal transfers fetched: {len(all_transfers)}")
    
    # Calculate net balances
    balances = {}
    for tx in all_transfers:
        from_addr = tx["from"].lower()
        to_addr = tx["to"].lower()
        value = int(tx["value"]) / 10**6  # BUIDL has 6 decimals
        
        # Subtract from sender
        if from_addr != "0x0000000000000000000000000000000000000000":
            balances[from_addr] = balances.get(from_addr, 0) - value
        
        # Add to receiver
        balances[to_addr] = balances.get(to_addr, 0) + value
    
    # Filter out zero/negative balances
    holders = {addr: bal for addr, bal in balances.items() if bal > 0.01}  # Minimum 0.01 BUIDL
    
    print(f"Found {len(holders)} holders with positive balances")
    
    return holders

def verify_balance_onchain(address, w3, contract):
    """Verify balance using Web3"""
    try:
        balance = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        return balance / 10**6
    except Exception as e:
        print(f"Error checking balance for {address}: {e}")
        return 0

def get_holders_with_verification():
    """Get holders and verify their balances on-chain"""
    
    # Step 1: Get holder list from transfers
    holders = get_holders_from_transfers()
    
    # Step 2: Verify balances using Web3
    print("\nVerifying balances on-chain...")
    
    # Use public RPC (Infura, Alchemy, or Ankr)
    # Let's use a public endpoint
    w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    
    if not w3.is_connected():
        print("Warning: Could not connect to Ethereum RPC")
        print("Returning unverified balances")
        return holders
    
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(BUIDL_CONTRACT),
        abi=ERC20_ABI
    )
    
    verified_holders = {}
    total = len(holders)
    
    for i, (address, calculated_balance) in enumerate(holders.items(), 1):
        if i % 10 == 0:
            print(f"Verified {i}/{total} addresses...")
        
        actual_balance = verify_balance_onchain(address, w3, contract)
        
        if actual_balance > 0:
            verified_holders[address] = actual_balance
        
        time.sleep(0.1)  # Be nice to the RPC
    
    print(f"\nVerification complete: {len(verified_holders)} holders confirmed")
    
    return verified_holders

def save_holders(holders, filename="holders.json"):
    """Save holder data to JSON"""
    data = {
        "timestamp": time.time(),
        "contract": BUIDL_CONTRACT,
        "total_holders": len(holders),
        "total_value": sum(holders.values()),
        "holders": [
            {"address": addr, "balance": bal}
            for addr, bal in sorted(holders.items(), key=lambda x: x[1], reverse=True)
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(holders)} holders to {filename}")
    
    # Also save as CSV for easy viewing
    import pandas as pd
    df = pd.DataFrame(data["holders"])
    df.to_csv(filename.replace('.json', '.csv'), index=False)
    print(f"Also saved as {filename.replace('.json', '.csv')}")

def main():
    print("=" * 80)
    print("BUIDL Holder Fetcher")
    print("=" * 80)
    print()
    
    holders = get_holders_with_verification()
    
    if holders:
        save_holders(holders)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total holders: {len(holders)}")
        print(f"Total BUIDL: ${sum(holders.values()):,.2f}")
        print(f"Average holding: ${sum(holders.values())/len(holders):,.2f}")
        print(f"Largest holder: ${max(holders.values()):,.2f}")
        print(f"Smallest holder: ${min(holders.values()):,.2f}")
        
        return holders
    else:
        print("ERROR: Could not fetch holders")
        return None

if __name__ == "__main__":
    main()
