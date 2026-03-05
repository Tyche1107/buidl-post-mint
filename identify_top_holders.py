#!/usr/bin/env python3
"""
Identify and analyze top BUIDL holders
Try to match addresses to known institutions
"""

import json

# Load holder data
with open('data/raw_holder_data.json') as f:
    data = json.load(f)

buidl_holders = data['buidl']['holders']

# Sort by balance
sorted_holders = sorted(buidl_holders.items(), key=lambda x: x[1], reverse=True)

print("=" * 70)
print("🔍 TOP 20 BUIDL HOLDERS ANALYSIS")
print("=" * 70)

# Known institutional addresses (from public sources)
known_addresses = {
    # Market makers (public info)
    "0xed71aa0da4fdba512ffa398fcff9db8c49a5cf72": "Suspected MM/Institution (largest holder)",
    "0x713742701e5aec2e31c272705d85aa8c3a51a258": "Suspected Institution #2",
    "0xe827abf9f462ac4f147753d86bc5f91e186e4e9c": "Suspected Institution #3",
    "0xb48cfe40ab635f6875b570d391dff805cf3acc32": "Suspected Institution #4",
    "0x12c0de58d3b720024324d5b216ddfe8b29adb0b4": "Suspected Institution #5",
    "0xf19a4fcc98c96a063ab06f3f5781e34a845a49e8": "Suspected Institution #6",
}

total_supply = sum(buidl_holders.values())

print(f"\n📊 Top 20 Holders:")
print(f"{'Rank':<6}{'Address':<44}{'Balance ($M)':<15}{'% of Supply':<12}{'Entity'}")
print("-" * 120)

for i, (addr, balance) in enumerate(sorted_holders[:20], 1):
    balance_usd = balance / 1e6
    pct = (balance / total_supply) * 100
    entity = known_addresses.get(addr, "Unknown")
    
    print(f"{i:<6}{addr:<44}${balance_usd:>12,.2f}{pct:>10.2f}%  {entity}")

# Analysis
top5_total = sum(bal for _, bal in sorted_holders[:5])
top10_total = sum(bal for _, bal in sorted_holders[:10])
top20_total = sum(bal for _, bal in sorted_holders[:20])

print(f"\n" + "=" * 70)
print("📈 CONCENTRATION ANALYSIS")
print("=" * 70)
print(f"Top 5 holders:  ${top5_total/1e6:,.2f}M ({top5_total/total_supply*100:.1f}%)")
print(f"Top 10 holders: ${top10_total/1e6:,.2f}M ({top10_total/total_supply*100:.1f}%)")
print(f"Top 20 holders: ${top20_total/1e6:,.2f}M ({top20_total/total_supply*100:.1f}%)")

# Holder size distribution
print(f"\n" + "=" * 70)
print("💰 HOLDER SIZE DISTRIBUTION")
print("=" * 70)

size_buckets = {
    "Whales (>$10M)": 0,
    "Large ($1M-$10M)": 0,
    "Medium ($100K-$1M)": 0,
    "Small (<$100K)": 0
}

for addr, balance in buidl_holders.items():
    balance_usd = balance / 1e6
    if balance_usd >= 10:
        size_buckets["Whales (>$10M)"] += 1
    elif balance_usd >= 1:
        size_buckets["Large ($1M-$10M)"] += 1
    elif balance_usd >= 0.1:
        size_buckets["Medium ($100K-$1M)"] += 1
    else:
        size_buckets["Small (<$100K)"] += 1

for category, count in size_buckets.items():
    pct = (count / len(buidl_holders)) * 100
    print(f"{category:<25} {count:>3} holders ({pct:>5.1f}%)")

# Check for DeFi patterns (addresses with many interactions)
print(f"\n" + "=" * 70)
print("🔍 POTENTIAL DEFI USERS (HEURISTIC)")
print("=" * 70)
print("Note: True DeFi analysis requires checking protocol contract interactions")
print("This is a simplified heuristic based on holder patterns")

# Addresses with "suspicious" patterns (round numbers, etc)
defi_candidates = []
for addr, balance in buidl_holders.items():
    balance_usd = balance / 1e6
    # Small holders more likely to be DeFi users
    if 0.01 < balance_usd < 10:
        defi_candidates.append((addr, balance_usd))

print(f"\nPotential DeFi-active holders: {len(defi_candidates)} / {len(buidl_holders)}")
print(f"  (Heuristic: $10K - $10M range)")

# Save analysis
output = {
    "top_20_holders": [
        {"rank": i+1, "address": addr, "balance_usd": bal/1e6, "pct_supply": (bal/total_supply)*100}
        for i, (addr, bal) in enumerate(sorted_holders[:20])
    ],
    "concentration": {
        "top_5_pct": (top5_total/total_supply)*100,
        "top_10_pct": (top10_total/total_supply)*100,
        "top_20_pct": (top20_total/total_supply)*100
    },
    "size_distribution": size_buckets,
    "total_holders": len(buidl_holders),
    "total_supply_usd": total_supply / 1e6
}

with open('data/holder_deep_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Analysis saved to data/holder_deep_analysis.json")
