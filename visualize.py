#!/usr/bin/env python3
"""
Create visualizations for BUIDL holder analysis
- Category distribution charts
- Sankey diagram showing flow from purchase to current state
- Sybil cluster network graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_analysis_data(filepath="holder_analysis.json"):
    """Load the analysis results"""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_category_distribution(df, output_dir="./"):
    """Create category distribution charts"""
    
    # Count by category
    category_counts = df['category'].value_counts()
    
    # Calculate value by category
    category_values = df.groupby('category')['buidl_balance'].sum()
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Count distribution
    colors = sns.color_palette("husl", len(category_counts))
    category_counts.plot(kind='bar', ax=ax1, color=colors)
    ax1.set_title('BUIDL Holders by Behavior Category', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Category', fontsize=12)
    ax1.set_ylabel('Number of Holders', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    
    # Add percentage labels
    total = len(df)
    for i, (cat, count) in enumerate(category_counts.items()):
        pct = (count / total) * 100
        ax1.text(i, count + 0.5, f'{count}\n({pct:.1f}%)', 
                ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Value distribution
    category_values.plot(kind='bar', ax=ax2, color=colors)
    ax2.set_title('BUIDL Value by Behavior Category', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Category', fontsize=12)
    ax2.set_ylabel('Total Value (USD)', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels
    total_value = df['buidl_balance'].sum()
    for i, (cat, value) in enumerate(category_values.items()):
        pct = (value / total_value) * 100
        ax2.text(i, value + max(category_values) * 0.02, 
                f'${value:,.0f}\n({pct:.1f}%)', 
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/category_distribution.png", dpi=300, bbox_inches='tight')
    print(f"Saved category_distribution.png")
    plt.close()

def create_sankey_diagram(df, output_dir="./"):
    """Create Sankey diagram showing holder journey"""
    
    # Define the flow: Acquisition -> Current Behavior
    # For simplicity, we'll show: All Holders -> Category
    
    categories = df['category'].unique().tolist()
    
    # Create nodes
    nodes = ['BUIDL Acquisition'] + categories
    node_colors = ['#3498db'] + sns.color_palette("husl", len(categories)).as_hex()
    
    # Create links
    source = []
    target = []
    value = []
    link_colors = []
    
    for i, category in enumerate(categories):
        count = len(df[df['category'] == category])
        source.append(0)  # From "BUIDL Acquisition"
        target.append(i + 1)  # To category
        value.append(count)
        # Semi-transparent version of category color
        color = node_colors[i + 1]
        link_colors.append(f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.4)')
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = nodes,
            color = node_colors
        ),
        link = dict(
            source = source,
            target = target,
            value = value,
            color = link_colors
        )
    )])
    
    fig.update_layout(
        title={
            'text': "BUIDL Holder Behavior Flow",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        font=dict(size=12),
        height=600,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    fig.write_html(f"{output_dir}/sankey_flow.html")
    fig.write_image(f"{output_dir}/sankey_flow.png", width=1200, height=600)
    print(f"Saved sankey_flow.html and sankey_flow.png")

def create_holder_table(df, output_dir="./"):
    """Create a detailed table of holders"""
    
    # Select key columns
    table_df = df[[
        'address', 'category', 'buidl_balance', 
        'total_txs', 'buidl_transfers_out', 'unique_counterparties'
    ]].copy()
    
    # Rename columns
    table_df.columns = [
        'Address', 'Category', 'BUIDL Balance (USD)', 
        'Total Txs', 'BUIDL Transfers Out', 'Unique Counterparties'
    ]
    
    # Sort by balance
    table_df = table_df.sort_values('BUIDL Balance (USD)', ascending=False)
    
    # Format address
    table_df['Address'] = table_df['Address'].apply(lambda x: f"{x[:6]}...{x[-4:]}")
    
    # Save as CSV
    table_df.to_csv(f"{output_dir}/holder_details.csv", index=False)
    
    # Create a nice HTML table for the report
    html_table = table_df.to_html(index=False, classes='holder-table', border=0)
    
    with open(f"{output_dir}/holder_table.html", 'w') as f:
        f.write(f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .holder-table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0;
                }}
                .holder-table th {{
                    background-color: #3498db;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                }}
                .holder-table td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }}
                .holder-table tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <h2>BUIDL Holder Details</h2>
            {html_table}
        </body>
        </html>
        """)
    
    print(f"Saved holder_details.csv and holder_table.html")

def create_pie_charts(df, output_dir="./"):
    """Create pie charts for category distribution"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Pie chart by count
    category_counts = df['category'].value_counts()
    colors = sns.color_palette("husl", len(category_counts))
    
    ax1.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Holder Distribution by Count', fontsize=14, fontweight='bold', pad=20)
    
    # Pie chart by value
    category_values = df.groupby('category')['buidl_balance'].sum()
    
    ax2.pie(category_values.values, labels=category_values.index, autopct='%1.1f%%',
            colors=colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('BUIDL Value Distribution by Category', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pie_charts.png", dpi=300, bbox_inches='tight')
    print(f"Saved pie_charts.png")
    plt.close()

def create_top_holders_chart(df, output_dir="./", top_n=10):
    """Create chart of top holders"""
    
    top_holders = df.nlargest(top_n, 'buidl_balance')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create horizontal bar chart
    colors_map = {cat: color for cat, color in zip(
        df['category'].unique(), 
        sns.color_palette("husl", len(df['category'].unique()))
    )}
    
    colors = [colors_map[cat] for cat in top_holders['category']]
    
    y_pos = range(len(top_holders))
    ax.barh(y_pos, top_holders['buidl_balance'], color=colors)
    
    # Format addresses for labels
    labels = [f"{addr[:6]}...{addr[-4:]}" for addr in top_holders['address']]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    
    ax.set_xlabel('BUIDL Balance (USD)', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} BUIDL Holders', fontsize=14, fontweight='bold')
    
    # Add value labels
    for i, (idx, row) in enumerate(top_holders.iterrows()):
        ax.text(row['buidl_balance'] + max(top_holders['buidl_balance']) * 0.01, 
                i, f"${row['buidl_balance']:,.0f}\n({row['category']})",
                va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/top_holders.png", dpi=300, bbox_inches='tight')
    print(f"Saved top_holders.png")
    plt.close()

def main():
    print("=" * 80)
    print("BUIDL Holder Visualization Generator")
    print("=" * 80)
    print()
    
    # Load data
    print("Loading analysis data...")
    df = pd.read_csv("holder_analysis.csv")
    
    print(f"Loaded {len(df)} holders")
    print()
    
    # Create output directory for charts
    import os
    os.makedirs("charts", exist_ok=True)
    
    # Generate all visualizations
    print("Generating visualizations...")
    
    create_category_distribution(df, "charts")
    create_pie_charts(df, "charts")
    create_sankey_diagram(df, "charts")
    create_top_holders_chart(df, "charts")
    create_holder_table(df, "charts")
    
    print()
    print("=" * 80)
    print("Visualization complete!")
    print("All charts saved in ./charts/ directory")
    print("=" * 80)

if __name__ == "__main__":
    main()
