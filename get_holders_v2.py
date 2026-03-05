#!/usr/bin/env python3
"""
Get BUIDL holders - Version 2
Use Web3 to query events directly, with fallback to known holders
"""

import requests
import json
import time
from web3 import Web3

BUIDL_CONTRACT = "0x7712c34205737192402172409a8f7ccef8aa2aec"
ETHERSCAN_API_KEY = "413E91H5PDDZYTVRY8AMK4D7FVTE65Z989"  # Try newer key

# Try multiple RPC endpoints
RPC_ENDPOINTS = [
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://ethereum.publicnode.com",
    "https://1rpc.io/eth",
]

def get_token_holders_via_etherscan_page():
    """
    Get holders by querying Etherscan's token holder list endpoint
    """
    print("Attempting to get holders from Etherscan token page...")
    
    # Etherscan has a token holder list page, but it's not in the public API
    # Let's try the token info endpoint first
    
    url = "https://api.etherscan.io/api"
    params = {
        "module": "token",
        "action": "tokeninfo",
        "contractaddress": BUIDL_CONTRACT,
        "apikey": ETHERSCAN_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    print(f"Token info response: {data}")
    
    # Try to get holder count
    if data.get("status") == "1":
        result = data.get("result", [])
        if result:
            print(f"Token: {result[0].get('name', 'Unknown')}")
            print(f"Total Supply: {result[0].get('totalSupply', 'Unknown')}")
    
    return None

def get_transfer_events_web3(w3, contract_address, from_block=0, to_block='latest'):
    """Get Transfer events using Web3"""
    
    # ERC20 Transfer event signature
    transfer_event_signature = Web3.keccak(text="Transfer(address,address,uint256)").hex()
    
    print(f"Querying Transfer events from block {from_block} to {to_block}...")
    
    # Get logs in chunks (to avoid timeouts)
    chunk_size = 1000000  # 1M blocks
    current_block = from_block
    
    if to_block == 'latest':
        to_block = w3.eth.block_number
    
    all_logs = []
    
    while current_block < to_block:
        chunk_end = min(current_block + chunk_size, to_block)
        
        print(f"Fetching logs: blocks {current_block} to {chunk_end}")
        
        try:
            logs = w3.eth.get_logs({
                'fromBlock': current_block,
                'toBlock': chunk_end,
                'address': Web3.to_checksum_address(contract_address),
                'topics': [transfer_event_signature]
            })
            
            all_logs.extend(logs)
            print(f"  Found {len(logs)} transfers in this chunk")
            
        except Exception as e:
            print(f"  Error fetching logs: {e}")
            # Try smaller chunk
            if chunk_size > 10000:
                chunk_size = chunk_size // 10
                continue
        
        current_block = chunk_end + 1
        time.sleep(0.5)  # Be nice to the RPC
    
    return all_logs

def process_transfer_logs(logs):
    """Process Transfer events to calculate balances"""
    
    balances = {}
    
    for log in logs:
        # Decode the Transfer event
        # topics[0] = event signature
        # topics[1] = from address
        # topics[2] = to address
        # data = value
        
        from_addr = '0x' + log['topics'][1].hex()[-40:]
        to_addr = '0x' + log['topics'][2].hex()[-40:]
        value = int(log['data'].hex(), 16) / 10**6  # BUIDL has 6 decimals
        
        # Update balances
        if from_addr != '0x0000000000000000000000000000000000000000':
            balances[from_addr.lower()] = balances.get(from_addr.lower(), 0) - value
        
        balances[to_addr.lower()] = balances.get(to_addr.lower(), 0) + value
    
    # Filter positive balances
    holders = {addr: bal for addr, bal in balances.items() if bal > 0.01}
    
    return holders

def try_multiple_rpcs():
    """Try connecting to multiple RPC endpoints"""
    
    for rpc in RPC_ENDPOINTS:
        print(f"Trying RPC: {rpc}")
        try:
            w3 = Web3(Web3.HTTPProvider(rpc))
            if w3.is_connected():
                print(f"✓ Connected to {rpc}")
                print(f"  Current block: {w3.eth.block_number}")
                return w3
        except Exception as e:
            print(f"✗ Failed to connect to {rpc}: {e}")
    
    return None

def get_buidl_creation_block():
    """
    Get the block when BUIDL contract was deployed
    This helps limit our search range
    """
    
    # BUIDL was deployed recently (2024/2025)
    # Let's check Etherscan for the creation tx
    
    url = "https://api.etherscan.io/api"
    params = {
        "module": "contract",
        "action": "getcontractcreation",
        "contractaddresses": BUIDL_CONTRACT,
        "apikey": ETHERSCAN_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1":
            result = data.get("result", [])
            if result:
                creation_tx = result[0].get("txHash")
                print(f"Contract creation tx: {creation_tx}")
                
                # Get the block number of creation
                w3 = try_multiple_rpcs()
                if w3:
                    tx = w3.eth.get_transaction(creation_tx)
                    return tx['blockNumber']
    except Exception as e:
        print(f"Could not get creation block: {e}")
    
    # Fallback: BUIDL launched in March 2024 ≈ block 19,000,000
    return 19000000

def use_known_holders_approach():
    """
    For a quick analysis, we can use known large holders and market data
    Since BUIDL has only 56 holders as stated, we can manually identify key ones
    """
    
    print("\n" + "=" * 80)
    print("Alternative Approach: Using known BUIDL ecosystem data")
    print("=" * 80)
    
    # Known facts from the brief:
    # - 56 holders total
    # - $171.8M on-chain market cap (Ethereum)
    # - Recent UniswapX integration (Feb 11, 2026)
    # - Market makers: Flowdesk, Tokka Labs, Wintermute
    
    # Let's create a sample dataset based on typical RWA distribution
    # We'll mark this as "SAMPLE" and note that real data is needed
    
    print("\nNote: Creating sample dataset for demonstration")
    print("Real holder addresses need to be obtained from:")
    print("1. Etherscan token holders page (manual)")
    print("2. Dune Analytics query")
    print("3. TheGraph subgraph")
    print()
    
    # For now, let's create the structure and note where real data is needed
    sample_holders = {
        # Market makers (known)
        "0x...flowdesk": 15000000,  # Placeholder
        "0x...tokka": 12000000,
        "0x...wintermute": 10000000,
        # Large institutional holders
        "0x...holder1": 8000000,
        "0x...holder2": 6000000,
        # Medium holders
        **{f"0x...holder{i}": 2000000 for i in range(3, 15)},
        # Smaller holders
        **{f"0x...holder{i}": 500000 for i in range(15, 56)},
    }
    
    print(f"Sample dataset: {len(sample_holders)} holders")
    print(f"Total value: ${sum(sample_holders.values()):,.2f}")
    
    return sample_holders

def main():
    print("=" * 80)
    print("BUIDL Holder Fetcher v2")
    print("=" * 80)
    print()
    
    # Try to get creation block
    creation_block = get_buidl_creation_block()
    print(f"BUIDL contract deployed at block: {creation_block}")
    print()
    
    # Try Web3 approach
    w3 = try_multiple_rpcs()
    
    if w3:
        print("\nAttempting to fetch transfer events...")
        try:
            # Get BUIDL creation to current
            logs = get_transfer_events_web3(w3, BUIDL_CONTRACT, creation_block, 'latest')
            
            if logs:
                print(f"\nProcessing {len(logs)} transfer events...")
                holders = process_transfer_logs(logs)
                
                if holders:
                    # Save results
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
                    
                    with open("holders.json", 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    print(f"\n✓ Success! Found {len(holders)} holders")
                    print(f"  Total BUIDL: ${sum(holders.values()):,.2f}")
                    print(f"  Saved to holders.json")
                    
                    return holders
        except Exception as e:
            print(f"Error with Web3 approach: {e}")
    
    # If all else fails, create sample data
    print("\n" + "!" * 80)
    print("Unable to fetch real holder data via API")
    print("Creating sample dataset for analysis framework demonstration")
    print("!" * 80)
    
    holders = use_known_holders_approach()
    
    # Save sample data
    data = {
        "timestamp": time.time(),
        "contract": BUIDL_CONTRACT,
        "total_holders": len(holders),
        "total_value": sum(holders.values()),
        "note": "SAMPLE DATA - Replace with real addresses from Etherscan/Dune",
        "holders": [
            {"address": addr, "balance": bal}
            for addr, bal in sorted(holders.items(), key=lambda x: x[1], reverse=True)
        ]
    }
    
    with open("holders_sample.json", 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSample data saved to holders_sample.json")
    print("\nNext steps:")
    print("1. Get real addresses from Etherscan: https://etherscan.io/token/" + BUIDL_CONTRACT + "#balances")
    print("2. Or use Dune Analytics query")
    print("3. Replace sample addresses with real ones")
    
    return holders

if __name__ == "__main__":
    main()
