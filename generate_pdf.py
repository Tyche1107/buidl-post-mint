#!/usr/bin/env python3
"""
Generate professional PDF report from markdown
"""

import markdown
import os
from datetime import datetime

def md_to_html_with_images(md_file, output_html):
    """Convert markdown to HTML with embedded images"""
    
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )
    
    # Create professional HTML template
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BlackRock BUIDL Holder Analysis</title>
    <style>
        @page {{
            size: letter;
            margin: 1in;
        }}
        
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #1a1a1a;
            font-size: 28px;
            font-weight: bold;
            margin-top: 0;
            margin-bottom: 10px;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }}
        
        h2 {{
            color: #0066cc;
            font-size: 20px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }}
        
        h3 {{
            color: #333;
            font-size: 16px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        h4 {{
            color: #666;
            font-size: 14px;
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 8px;
        }}
        
        p {{
            margin-bottom: 12px;
            text-align: justify;
        }}
        
        ul, ol {{
            margin-bottom: 15px;
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 6px;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 13px;
        }}
        
        th {{
            background-color: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        tr:hover {{
            background-color: #f0f0f0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            display: block;
            border: 1px solid #ddd;
            padding: 5px;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-left: 4px solid #0066cc;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }}
        
        blockquote {{
            border-left: 4px solid #0066cc;
            margin-left: 0;
            padding-left: 20px;
            color: #666;
            font-style: italic;
        }}
        
        .executive-summary {{
            background-color: #f0f8ff;
            border: 2px solid #0066cc;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .key-finding {{
            background-color: #fff8dc;
            border-left: 4px solid #ffa500;
            padding: 15px;
            margin: 15px 0;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            font-size: 11px;
            color: #666;
            text-align: center;
        }}
        
        .confidential {{
            color: #cc0000;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        
        .page-break {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
    {html_content}
    
    <div class="footer">
        <p>Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        <p>Decentralized Computing Lab | University of Washington | HasciDB Project</p>
        <p class="confidential">CONFIDENTIAL - For BlackRock Digital Assets Team Only</p>
    </div>
</body>
</html>
"""
    
    with open(output_html, 'w') as f:
        f.write(html_template)
    
    print(f"HTML report saved: {output_html}")

def html_to_pdf(html_file, output_pdf):
    """Convert HTML to PDF using weasyprint"""
    try:
        from weasyprint import HTML
        
        print(f"Converting {html_file} to PDF...")
        HTML(html_file).write_pdf(output_pdf)
        print(f"✓ PDF report saved: {output_pdf}")
        return True
    except Exception as e:
        print(f"Error converting to PDF with weasyprint: {e}")
        print("\nAlternative: Use browser to print HTML to PDF")
        print(f"Open {html_file} in a browser and use Print → Save as PDF")
        return False

def create_cover_page():
    """Create a professional cover page"""
    cover_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: letter;
            margin: 0;
        }}
        
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            height: 11in;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #0066cc 0%, #004999 100%);
            color: white;
        }}
        
        .cover-content {{
            text-align: center;
            padding: 40px;
        }}
        
        h1 {{
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 20px;
            line-height: 1.2;
        }}
        
        h2 {{
            font-size: 24px;
            font-weight: 300;
            margin-bottom: 40px;
            opacity: 0.9;
        }}
        
        .subtitle {{
            font-size: 28px;
            font-weight: 600;
            margin: 30px 0;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }}
        
        .metadata {{
            margin-top: 60px;
            font-size: 16px;
            line-height: 2;
        }}
        
        .logo {{
            font-size: 72px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="cover-content">
        <div class="logo">📊</div>
        <h1>Only 18 of BlackRock BUIDL's<br>56 Ethereum Holders<br>Are Actually Holding</h1>
        <div class="subtitle">贝莱德BUIDL的56个以太坊持有者中<br>只有18个在真正持有</div>
        <h2>On-chain Behavioral Analysis of BUIDL Token Holders</h2>
        <div class="metadata">
            <p><strong>Prepared for:</strong> Robert Mitchnick</p>
            <p>Head of Digital Assets, BlackRock</p>
            <p style="margin-top: 40px;"><strong>Research Team:</strong></p>
            <p>Decentralized Computing Lab</p>
            <p>University of Washington</p>
            <p>Wei Cai Lab | HasciDB Project</p>
            <p style="margin-top: 40px;">{datetime.now().strftime("%B %d, %Y")}</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open("cover_page.html", "w") as f:
        f.write(cover_html)
    
    print("Cover page created: cover_page.html")

def main():
    print("=" * 80)
    print("PDF Report Generator")
    print("=" * 80)
    print()
    
    # Create cover page
    print("Creating cover page...")
    create_cover_page()
    print()
    
    # Convert markdown to HTML
    print("Converting Markdown to HTML...")
    md_to_html_with_images("report.md", "report.html")
    print()
    
    # Try to create PDF
    print("Generating PDF...")
    success = html_to_pdf("report.html", "BUIDL_Holder_Analysis_Report.pdf")
    
    if success:
        print("\n✓ PDF generation successful!")
        print("\nOutput files:")
        print("  - BUIDL_Holder_Analysis_Report.pdf (main report)")
        print("  - report.html (HTML version)")
        print("  - cover_page.html (cover page)")
    else:
        print("\nManual PDF creation required:")
        print("1. Open report.html in a web browser")
        print("2. Use Print → Save as PDF")
        print("3. Or use: pandoc report.md -o report.pdf")
    
    # Show file sizes
    print("\n" + "=" * 80)
    print("Generated Files:")
    print("=" * 80)
    os.system("ls -lh *.html *.pdf 2>/dev/null | tail -n +2 || echo 'No PDFs yet (weasyprint may need manual installation)'")

if __name__ == "__main__":
    main()
