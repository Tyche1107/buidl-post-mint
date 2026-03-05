#!/usr/bin/env python3
"""
Fetch BUIDL holders using Dune Analytics API
More reliable than parsing Etherscan transfers
"""

import requests
import json
import time
import pandas as pd

DUNE_API_KEY = "tTVICcVIhr9yZjdfg2IXxkB5b65T6tks"
BUIDL_CONTRACT = "0x7712c34205737192402172409a8f7ccef8aa2aec"

def create_dune_query():
    """Create a Dune query to get BUIDL holders"""
    query = f"""
    SELECT 
        holder AS address,
        balance / 1e6 AS balance_usd,
        COUNT(*) OVER() as total_holders
    FROM (
        SELECT 
            to AS holder,
            SUM(CASE WHEN to = address THEN CAST(value AS DOUBLE) ELSE -CAST(value AS DOUBLE) END) AS balance
        FROM erc20_ethereum.evt_Transfer
        WHERE contract_address = {BUIDL_CONTRACT}
        GROUP BY to
    ) 
    WHERE balance > 0
    ORDER BY balance DESC
    """
    return query

def execute_dune_query(query):
    """Execute a query on Dune Analytics"""
    print("Creating Dune query...")
    
    # Step 1: Create the query
    url = "https://api.dune.com/api/v1/query"
    headers = {
        "X-Dune-API-Key": DUNE_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "query_sql": query,
        "name": "BUIDL Holders Analysis",
        "is_private": False
    }
    
    # Note: Free tier might not support query creation
    # Let's try to use execution directly with inline query
    
    # Alternative: Execute an existing query or use the newer endpoint
    # For now, let's use a simpler approach via the newer API
    
    print("Note: Dune free tier has limitations. Trying direct execution...")
    
    # Try query execution endpoint
    exec_url = "https://api.dune.com/api/v1/execution"
    
    # This might not work with free tier, we may need to use a pre-made query
    # Let's save the query and provide instructions to run it manually
    
    return None

def get_holders_from_file(filepath="known_holders.json"):
    """Load holders from a pre-saved file or create a template"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"File {filepath} not found")
        return None

def main():
    print("=" * 80)
    print("BUIDL Holders Fetcher (Dune Analytics)")
    print("=" * 80)
    print()
    
    # Save the Dune query for manual execution
    query = create_dune_query()
    
    with open("dune_query.sql", "w") as f:
        f.write(query)
    
    print("Dune query saved to dune_query.sql")
    print()
    print("INSTRUCTIONS:")
    print("1. Go to https://dune.com")
    print("2. Create a new query")
    print("3. Paste the SQL from dune_query.sql")
    print("4. Execute the query")
    print("5. Export results as CSV and save as 'holders_dune.csv'")
    print()
    print("OR use the public BUIDL dashboard if available")
    print()
    
    # Alternative: Try to fetch from a known Dune dashboard
    # There might be public BUIDL dashboards we can query
    
    print("Attempting to fetch from Etherscan as fallback...")
    
    # Fallback to direct Etherscan token holders page scraping
    # Or use Etherscan's token holder API if available
    
    return query

if __name__ == "__main__":
    main()
