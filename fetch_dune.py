#!/usr/bin/env python3
"""
Fetch BUIDL holders using Dune Analytics API
Most reliable method for getting current token holder balances
"""

import requests
import json
import time
import pandas as pd

DUNE_API_KEY = "tTVICcVIhr9yZjdfg2IXxkB5b65T6tks"
BUIDL_CONTRACT = "0x7712c34205737192402172409a8f7ccef8aa2aec"

def execute_dune_query():
    """
    Create and execute a Dune query for BUIDL holders
    """
    
    # SQL query to get BUIDL token holders
    sql_query = f"""
WITH transfers AS (
    SELECT 
        "to" AS address,
        CAST(value AS DOUBLE) AS amount
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = {BUIDL_CONTRACT}
    
    UNION ALL
    
    SELECT 
        "from" AS address,
        -CAST(value AS DOUBLE) AS amount
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = {BUIDL_CONTRACT}
        AND "from" != 0x0000000000000000000000000000000000000000
),

balances AS (
    SELECT 
        address,
        SUM(amount) / 1e6 AS balance_usd
    FROM transfers
    GROUP BY address
    HAVING SUM(amount) > 0
)

SELECT 
    address,
    balance_usd,
    ROW_NUMBER() OVER (ORDER BY balance_usd DESC) as rank
FROM balances
ORDER BY balance_usd DESC
"""
    
    print("Creating Dune query...")
    print("SQL Query:")
    print(sql_query)
    print()
    
    # Step 1: Create a query
    create_url = "https://api.dune.com/api/v1/query"
    headers = {
        "X-DUNE-API-KEY": DUNE_API_KEY,
        "Content-Type": "application/json"
    }
    
    create_payload = {
        "query_sql": sql_query,
        "name": "BUIDL Token Holders",
        "is_private": False
    }
    
    print("Attempting to create query on Dune...")
    
    try:
        response = requests.post(create_url, headers=headers, json=create_payload)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            query_id = data.get("query_id")
            print(f"✓ Query created with ID: {query_id}")
            
            # Step 2: Execute the query
            exec_url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
            
            print("Executing query...")
            exec_response = requests.post(exec_url, headers=headers)
            
            if exec_response.status_code == 200:
                exec_data = exec_response.json()
                execution_id = exec_data.get("execution_id")
                print(f"✓ Execution started: {execution_id}")
                
                # Step 3: Poll for results
                return poll_query_results(query_id, execution_id)
            else:
                print(f"✗ Execution failed: {exec_response.text}")
        else:
            print(f"✗ Query creation failed")
            print("This might be due to API tier limitations")
    
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def poll_query_results(query_id, execution_id, max_wait=300):
    """Poll for query results"""
    
    headers = {
        "X-DUNE-API-KEY": DUNE_API_KEY
    }
    
    results_url = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
    
    print("Waiting for query results...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(results_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            state = data.get("state")
            
            print(f"  State: {state}")
            
            if state == "QUERY_STATE_COMPLETED":
                print("✓ Query completed!")
                rows = data.get("result", {}).get("rows", [])
                return rows
            elif state == "QUERY_STATE_FAILED":
                print(f"✗ Query failed: {data.get('error', 'Unknown error')}")
                return None
            
            time.sleep(5)  # Wait before polling again
        else:
            print(f"Error polling results: {response.text}")
            return None
    
    print("✗ Timeout waiting for results")
    return None

def use_existing_query():
    """
    Alternative: Use an existing public query if one exists
    Let's check if there's a public BUIDL dashboard
    """
    
    print("Attempting to find existing BUIDL queries on Dune...")
    
    # Common public query IDs for BlackRock BUIDL might exist
    # Let's try to search
    
    # For now, return instructions
    print("\nAlternative approach:")
    print("1. Go to https://dune.com/discover/content/trending")
    print("2. Search for 'BlackRock BUIDL' or 'BUIDL token'")
    print("3. If a query exists, get its ID from the URL")
    print("4. Use: https://api.dune.com/api/v1/query/{query_id}/results")
    
    return None

def save_manual_query_template():
    """Save SQL query for manual execution"""
    
    sql = f"""
-- BUIDL Token Holder Balances
-- Run this query on dune.com

WITH transfers AS (
    SELECT 
        "to" AS address,
        CAST(value AS DOUBLE) AS amount,
        evt_block_time,
        evt_tx_hash
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = {BUIDL_CONTRACT}
    
    UNION ALL
    
    SELECT 
        "from" AS address,
        -CAST(value AS DOUBLE) AS amount,
        evt_block_time,
        evt_tx_hash
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = {BUIDL_CONTRACT}
        AND "from" != 0x0000000000000000000000000000000000000000
),

balances AS (
    SELECT 
        address,
        SUM(amount) / 1e6 AS balance_usd,
        COUNT(*) AS num_transfers,
        MIN(evt_block_time) AS first_transfer,
        MAX(evt_block_time) AS last_transfer
    FROM transfers
    GROUP BY address
    HAVING SUM(amount) > 0
)

SELECT 
    address,
    balance_usd,
    num_transfers,
    first_transfer,
    last_transfer,
    ROW_NUMBER() OVER (ORDER BY balance_usd DESC) as rank
FROM balances
ORDER BY balance_usd DESC
LIMIT 100
"""
    
    with open("dune_buidl_query.sql", "w") as f:
        f.write(sql)
    
    print("SQL query saved to dune_buidl_query.sql")
    print("\nTo use:")
    print("1. Go to https://dune.com/queries")
    print("2. Create new query")
    print("3. Paste the SQL from dune_buidl_query.sql")
    print("4. Run the query")
    print("5. Export as CSV")

def main():
    print("=" * 80)
    print("BUIDL Holders via Dune Analytics")
    print("=" * 80)
    print()
    
    # Save manual query template
    save_manual_query_template()
    print()
    
    # Try API approach
    print("Attempting API-based query...")
    print("Note: Free tier may have limitations")
    print()
    
    results = execute_dune_query()
    
    if results:
        # Save results
        df = pd.DataFrame(results)
        df.to_csv("holders_dune.csv", index=False)
        df.to_json("holders_dune.json", orient="records", indent=2)
        
        print(f"\n✓ Success! Fetched {len(results)} holders")
        print(f"  Saved to holders_dune.csv and holders_dune.json")
        
        # Print summary
        if len(results) > 0:
            total_value = df['balance_usd'].sum()
            print(f"\nSummary:")
            print(f"  Total holders: {len(results)}")
            print(f"  Total value: ${total_value:,.2f}")
            print(f"  Largest holder: ${df['balance_usd'].max():,.2f}")
            print(f"  Average holding: ${total_value/len(results):,.2f}")
    else:
        print("\n" + "=" * 80)
        print("API approach unsuccessful")
        print("Please run the query manually on dune.com")
        print("=" * 80)

if __name__ == "__main__":
    main()
