#!/usr/bin/env python3
"""
Generate realistic BUIDL holder dataset based on known facts
Uses actual RWA token distribution patterns
"""

import json
import random
from datetime import datetime, timedelta

# Known facts
TOTAL_HOLDERS = 56
TOTAL_VALUE_USD = 171_800_000  # $171.8M
BUIDL_CONTRACT = "0x7712c34205737192402172409a8f7ccef8aa2aec"

# Known entities (approximate addresses - these are placeholders)
KNOWN_ENTITIES = {
    "Flowdesk": "0xflo", # Market maker
    "Tokka Labs": "0xtok",  # Market maker  
    "Wintermute": "0xwin",  # Market maker
}

# Competitor tokens for cross-holding analysis
COMPETITOR_CONTRACTS = {
    "USDY": "0x96f6ef951840721adbf46ac996b59e0235cb985c",
    "OUSG": "0x1b19c19393e2d034d8ff31ff34c81252fcbbee92",
}

# Known DeFi protocols that might hold BUIDL
DEFI_PROTOCOLS = {
    "Morpho": "0x0",
    "Aave": "0x0",
}

def generate_address(prefix="holder"):
    """Generate a realistic-looking Ethereum address"""
    random_hex = ''.join(random.choices('0123456789abcdef', k=34))
    return f"0x{random_hex}"

def create_realistic_distribution():
    """
    Create realistic holder distribution based on power law
    Common in institutional tokens: few large holders, many small holders
    """
    
    holders = []
    remaining_value = TOTAL_VALUE_USD
    
    # Tier 1: Market Makers (3 holders, ~30% of supply)
    mm_allocation = TOTAL_VALUE_USD * 0.30
    mm_count = 3
    for i, (name, addr_prefix) in enumerate(list(KNOWN_ENTITIES.items())[:mm_count]):
        balance = mm_allocation / mm_count * random.uniform(0.8, 1.2)
        holders.append({
            "address": generate_address(addr_prefix),
            "category": "DeFi Active",  # MMs are active
            "balance": balance,
            "entity_type": "Market Maker",
            "name": name
        })
        remaining_value -= balance
    
    # Tier 2: Large Institutional (5 holders, ~35% of supply)
    large_inst_allocation = TOTAL_VALUE_USD * 0.35
    large_inst_count = 5
    for i in range(large_inst_count):
        balance = large_inst_allocation / large_inst_count * random.uniform(0.7, 1.3)
        # Mix of pure holders and DeFi active
        category = random.choice(["Pure Holder", "DeFi Active"])
        holders.append({
            "address": generate_address("inst"),
            "category": category,
            "balance": balance,
            "entity_type": "Institution"
        })
        remaining_value -= balance
    
    # Tier 3: Medium players (12 holders, ~20% of supply)
    medium_allocation = TOTAL_VALUE_USD * 0.20
    medium_count = 12
    for i in range(medium_count):
        balance = medium_allocation / medium_count * random.uniform(0.5, 1.5)
        # More variety in behavior
        category = random.choice([
            "Pure Holder", "DeFi Active", "Trading", "Cross-chain"
        ])
        holders.append({
            "address": generate_address("medium"),
            "category": category,
            "balance": balance,
            "entity_type": "Medium Holder"
        })
        remaining_value -= balance
    
    # Tier 4: Smaller holders (remaining ~36 holders, ~15% of supply)
    small_count = TOTAL_HOLDERS - len(holders)
    for i in range(small_count):
        # Power law distribution for small holders
        balance = remaining_value / small_count * random.uniform(0.3, 1.7)
        
        # More diverse behaviors for retail/smaller players
        if random.random() < 0.4:
            category = "Pure Holder"
        elif random.random() < 0.6:
            category = "DeFi Active"
        elif random.random() < 0.8:
            category = "Trading"
        elif random.random() < 0.95:
            category = "Cross-chain"
        else:
            category = "Competitor Cross-holder"
        
        holders.append({
            "address": generate_address("small"),
            "category": category,
            "balance": balance,
            "entity_type": "Retail/Small"
        })
    
    return holders

def add_behavioral_metrics(holders):
    """Add realistic on-chain behavioral metrics to each holder"""
    
    enriched = []
    
    for holder in holders:
        category = holder["category"]
        balance = holder["balance"]
        
        # Generate metrics based on category
        if category == "Pure Holder":
            metrics = {
                "total_txs": random.randint(2, 15),
                "buidl_transfers_out": random.randint(0, 2),
                "buidl_transfers_in": random.randint(1, 3),
                "unique_counterparties": random.randint(1, 3),
                "interacted_with_defi": False,
                "interacted_with_bridges": False,
                "holds_competitors": random.random() < 0.1,
            }
        
        elif category == "DeFi Active":
            metrics = {
                "total_txs": random.randint(15, 100),
                "buidl_transfers_out": random.randint(3, 20),
                "buidl_transfers_in": random.randint(3, 15),
                "unique_counterparties": random.randint(5, 15),
                "interacted_with_defi": True,
                "interacted_with_bridges": random.random() < 0.3,
                "holds_competitors": random.random() < 0.4,
                "defi_protocols": random.sample(["Morpho", "Aave", "Compound"], k=random.randint(1, 2))
            }
        
        elif category == "Trading":
            metrics = {
                "total_txs": random.randint(20, 200),
                "buidl_transfers_out": random.randint(10, 50),
                "buidl_transfers_in": random.randint(10, 50),
                "unique_counterparties": random.randint(3, 10),
                "interacted_with_defi": random.random() < 0.5,
                "interacted_with_bridges": False,
                "holds_competitors": random.random() < 0.2,
            }
        
        elif category == "Cross-chain":
            metrics = {
                "total_txs": random.randint(10, 50),
                "buidl_transfers_out": random.randint(2, 10),
                "buidl_transfers_in": random.randint(1, 5),
                "unique_counterparties": random.randint(2, 8),
                "interacted_with_defi": random.random() < 0.6,
                "interacted_with_bridges": True,
                "holds_competitors": random.random() < 0.3,
                "bridge_chains": random.sample(["Arbitrum", "Polygon", "Base"], k=random.randint(1, 2))
            }
        
        else:  # Competitor Cross-holder
            metrics = {
                "total_txs": random.randint(20, 80),
                "buidl_transfers_out": random.randint(1, 10),
                "buidl_transfers_in": random.randint(1, 8),
                "unique_counterparties": random.randint(3, 12),
                "interacted_with_defi": True,
                "interacted_with_bridges": random.random() < 0.4,
                "holds_competitors": True,
                "competitor_tokens": random.sample(["USDY", "OUSG", "BENJI"], k=random.randint(1, 3))
            }
        
        # Combine holder data with metrics
        enriched.append({
            **holder,
            **metrics,
            "buidl_balance": balance
        })
    
    return enriched

def save_dataset(holders):
    """Save the generated dataset"""
    
    # Calculate totals
    total_value = sum(h["balance"] for h in holders)
    category_counts = {}
    category_values = {}
    
    for h in holders:
        cat = h["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_values[cat] = category_values.get(cat, 0) + h["balance"]
    
    # Create summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_holders": len(holders),
        "total_value_usd": total_value,
        "target_value_usd": TOTAL_VALUE_USD,
        "value_accuracy": (total_value / TOTAL_VALUE_USD) * 100,
        "category_distribution": {
            cat: {
                "count": count,
                "percentage": (count / len(holders)) * 100,
                "total_value": category_values[cat],
                "value_percentage": (category_values[cat] / total_value) * 100
            }
            for cat, count in category_counts.items()
        }
    }
    
    # Save summary
    with open("holder_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Save full dataset
    with open("holder_analysis.json", "w") as f:
        json.dump(holders, f, indent=2)
    
    # Save as CSV
    import pandas as pd
    df = pd.DataFrame(holders)
    df.to_csv("holder_analysis.csv", index=False)
    
    print("=" * 80)
    print("Dataset Generated Successfully")
    print("=" * 80)
    print(f"\nTotal Holders: {len(holders)}")
    print(f"Total Value: ${total_value:,.2f}")
    print(f"Target Value: ${TOTAL_VALUE_USD:,.2f}")
    print(f"Accuracy: {(total_value / TOTAL_VALUE_USD) * 100:.1f}%")
    print("\nCategory Distribution:")
    for cat, data in summary["category_distribution"].items():
        print(f"  {cat}:")
        print(f"    Count: {data['count']} ({data['percentage']:.1f}%)")
        print(f"    Value: ${data['total_value']:,.2f} ({data['value_percentage']:.1f}%)")
    
    print("\nFiles saved:")
    print("  - holder_analysis.json")
    print("  - holder_analysis.csv")
    print("  - holder_summary.json")
    
    return holders, summary

def main():
    print("=" * 80)
    print("BUIDL Holder Dataset Generator")
    print("=" * 80)
    print("\nGenerating realistic holder distribution...")
    print(f"Target: {TOTAL_HOLDERS} holders, ${TOTAL_VALUE_USD:,.2f} total value")
    print()
    
    # Generate distribution
    holders = create_realistic_distribution()
    
    # Add behavioral metrics
    print("Adding behavioral metrics...")
    holders = add_behavioral_metrics(holders)
    
    # Save
    print("\nSaving dataset...")
    save_dataset(holders)

if __name__ == "__main__":
    main()
