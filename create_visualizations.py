#!/usr/bin/env python3
"""
Create shocking visualizations for BlackRock BUIDL vs Ondo analysis
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'

# Load data
with open('data/shocking_analysis.json') as f:
    data = json.load(f)

# 1. Holder Count Comparison - Shocking Bar Chart
fig, ax = plt.subplots(figsize=(10, 6))

tokens = ['BlackRock\nBUILD', 'Ondo\nUSDY']
holders = [data['buidl_holders'], data['usdy_holders']]
colors = ['#1f77b4', '#ff7f0e']

bars = ax.bar(tokens, holders, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, holders)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

# Add shocking annotation
ax.annotate('11.3x MORE\nHOLDERS', 
            xy=(1, holders[1]), xytext=(0.5, holders[1] * 0.7),
            arrowprops=dict(arrowstyle='->', color='red', lw=3),
            fontsize=16, color='red', fontweight='bold',
            ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

ax.set_ylabel('Number of Holders', fontsize=13, fontweight='bold')
ax.set_title('BlackRock BUIDL vs Ondo USDY: Holder Count Gap\nSame TVL ($176M), 11x Fewer Clients', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/shocking_holder_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/shocking_holder_comparison.png")

# 2. TVL vs Holders Scatter Plot - Same Money, Different Reach
fig, ax = plt.subplots(figsize=(10, 7))

# Data points
tvls = [data['buidl_tvl'] / 1e6, data['usdy_tvl'] / 1e6]  # Convert to millions
holders_data = [data['buidl_holders'], data['usdy_holders']]

# Plot points
ax.scatter(holders_data[0], tvls[0], s=2000, alpha=0.6, color='#1f77b4', 
           edgecolors='black', linewidth=3, label='BlackRock BUIDL', zorder=5)
ax.scatter(holders_data[1], tvls[1], s=2000, alpha=0.6, color='#ff7f0e',
           edgecolors='black', linewidth=3, label='Ondo USDY', zorder=5)

# Add labels
ax.text(holders_data[0], tvls[0], 'BUIDL\n57 holders\n$176M', 
        ha='center', va='center', fontsize=11, fontweight='bold')
ax.text(holders_data[1], tvls[1], 'USDY\n643 holders\n$176M', 
        ha='center', va='center', fontsize=11, fontweight='bold')

# Draw arrow showing the gap
ax.annotate('', xy=(holders_data[1], tvls[1]), xytext=(holders_data[0], tvls[0]),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2))

ax.text((holders_data[0] + holders_data[1])/2, (tvls[0] + tvls[1])/2 + 10,
        'Same TVL\n11x more clients →',
        ha='center', fontsize=12, color='red', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='yellow', alpha=0.7))

ax.set_xlabel('Number of Holders', fontsize=13, fontweight='bold')
ax.set_ylabel('Total Value Locked ($ Millions)', fontsize=13, fontweight='bold')
ax.set_title('Capital Efficiency Gap: BUIDL vs USDY\nOndo Reached 11x More Clients with Same Capital',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11, loc='upper left')

# Set axis limits with padding
ax.set_xlim(0, holders_data[1] * 1.2)
ax.set_ylim(tvls[0] * 0.8, tvls[1] * 1.2)

plt.tight_layout()
plt.savefig('charts/tvl_vs_holders_scatter.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/tvl_vs_holders_scatter.png")

# 3. Market Penetration Comparison - Pie Charts Side by Side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# BUIDL concentration
buidl_data = [data['buidl_top10_concentration'], 100 - data['buidl_top10_concentration']]
buidl_labels = [f"Top 10\n({data['buidl_top10_concentration']:.1f}%)", 
                f"Others\n({100-data['buidl_top10_concentration']:.1f}%)"]
colors1 = ['#d62728', '#aaaaaa']

wedges1, texts1, autotexts1 = ax1.pie(buidl_data, labels=buidl_labels, autopct='%1.1f%%',
                                        colors=colors1, startangle=90, textprops={'fontsize': 11})
ax1.set_title('BlackRock BUIDL\nHighly Concentrated (Top 10: 82.8%)', 
              fontsize=12, fontweight='bold')

# USDY concentration
usdy_data = [data['usdy_top10_concentration'], 100 - data['usdy_top10_concentration']]
usdy_labels = [f"Top 10\n({data['usdy_top10_concentration']:.1f}%)", 
               f"Others\n({100-data['usdy_top10_concentration']:.1f}%)"]
colors2 = ['#d62728', '#aaaaaa']

wedges2, texts2, autotexts2 = ax2.pie(usdy_data, labels=usdy_labels, autopct='%1.1f%%',
                                        colors=colors2, startangle=90, textprops={'fontsize': 11})
ax2.set_title('Ondo USDY\nAlso Concentrated (Top 10: 91.0%)', 
              fontsize=12, fontweight='bold')

fig.suptitle('Supply Concentration: Both Highly Concentrated\nBut USDY Has Broader Base (643 vs 57 holders)',
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('charts/concentration_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/concentration_comparison.png")

# 4. Key Metrics Dashboard
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Title
fig.suptitle('BlackRock BUIDL vs Ondo USDY: The Shocking Truth', 
             fontsize=18, fontweight='bold', y=0.98)

# Metrics boxes
metrics = [
    {"title": "Total Value Locked", "buidl": "$176M", "usdy": "$176M", "winner": "TIE"},
    {"title": "Number of Holders", "buidl": "57", "usdy": "643", "winner": "USDY"},
    {"title": "Avg $ per Holder", "buidl": "$3.1M", "usdy": "$274K", "winner": "BUIDL"},
    {"title": "Top 10 Concentration", "buidl": "82.8%", "usdy": "91.0%", "winner": "TIE"},
    {"title": "Cross-Holding", "buidl": "0", "usdy": "0", "winner": "TIE"},
    {"title": "Market Strategy", "buidl": "Ultra-HNW", "usdy": "Broad Inst.", "winner": "DIFFERENT"},
]

y_start = 0.85
for i, metric in enumerate(metrics):
    y = y_start - i * 0.14
    
    # Metric title
    ax.text(0.05, y, metric['title'], fontsize=13, fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray'))
    
    # BUIDL value
    buidl_color = 'lightgreen' if metric['winner'] == 'BUIDL' else 'white'
    ax.text(0.35, y, metric['buidl'], fontsize=12, ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=buidl_color, edgecolor='blue', linewidth=2))
    
    # USDY value
    usdy_color = 'lightgreen' if metric['winner'] == 'USDY' else 'white'
    ax.text(0.55, y, metric['usdy'], fontsize=12, ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=usdy_color, edgecolor='orange', linewidth=2))
    
    # Winner indicator
    if metric['winner'] not in ['TIE', 'DIFFERENT']:
        ax.text(0.75, y, f"✓ {metric['winner']}", fontsize=11, color='green', fontweight='bold')
    elif metric['winner'] == 'TIE':
        ax.text(0.75, y, "—", fontsize=11, ha='center')

# Column headers
ax.text(0.35, 0.92, 'BUIDL', fontsize=14, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue'))
ax.text(0.55, 0.92, 'USDY', fontsize=14, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow'))

# Bottom conclusion
conclusion = ("CONCLUSION: Ondo captured 11x more institutional clients with the same capital.\n"
              "BlackRock's ultra-institutional approach may be limiting broader adoption.")
ax.text(0.5, 0.08, conclusion, fontsize=12, ha='center', style='italic',
        bbox=dict(boxstyle='round,pad=1', facecolor='lightyellow', edgecolor='red', linewidth=3))

plt.tight_layout()
plt.savefig('charts/metrics_dashboard.png', dpi=300, bbox_inches='tight')
print("✅ Created: charts/metrics_dashboard.png")

print("\n✅ All visualizations created successfully!")
print("📁 Saved to: charts/")
