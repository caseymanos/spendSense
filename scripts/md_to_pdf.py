#!/usr/bin/env python3
"""
Convert markdown files to PDF using macOS built-in tools.
"""

import sys
import subprocess
from pathlib import Path
import re


def apply_inline_formatting(text: str) -> str:
    """Apply inline markdown formatting (bold, italic, code)."""
    # Convert bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Convert italic (avoid matching already converted bold)
    text = re.sub(r'(?<!\*)\*([^\*]+?)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'<em>\1</em>', text)

    # Convert inline code
    text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)

    return text


def markdown_to_html(md_content: str, title: str = "Document") -> str:
    """Convert markdown to basic HTML with styling."""
    lines = md_content.split('\n')
    html_lines = []
    in_code_block = False
    in_list = False
    list_type = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                html_lines.append('<pre><code>')
            else:
                in_code_block = False
                html_lines.append('</code></pre>')
            i += 1
            continue

        if in_code_block:
            html_lines.append(line)
            i += 1
            continue

        # Handle headers
        if stripped.startswith('#'):
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
            header_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2)
                # Apply inline formatting to header text
                text = apply_inline_formatting(text)
                html_lines.append(f'<h{level}>{text}</h{level}>')
                i += 1
                continue

        # Handle lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            item = stripped[2:]
            item = apply_inline_formatting(item)
            html_lines.append(f'<li>{item}</li>')
            i += 1
            continue
        elif re.match(r'^\d+\.\s', stripped):
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            item = re.sub(r'^\d+\.\s+', '', stripped)
            item = apply_inline_formatting(item)
            html_lines.append(f'<li>{item}</li>')
            i += 1
            continue
        else:
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False

        # Handle horizontal rules
        if stripped in ['---', '***', '___']:
            html_lines.append('<hr>')
            i += 1
            continue

        # Handle empty lines
        if not stripped:
            html_lines.append('<br>')
            i += 1
            continue

        # Handle paragraphs
        text = apply_inline_formatting(line)
        html_lines.append(f'<p>{text}</p>')
        i += 1

    # Close any open lists
    if in_list:
        html_lines.append(f'</{list_type}>')

    html = '\n'.join(html_lines)

    # Wrap in full HTML document
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #7f8c8d;
                margin-top: 20px;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            pre code {{
                padding: 0;
                background: none;
            }}
            ul, ol {{
                padding-left: 30px;
            }}
            li {{
                margin: 5px 0;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            strong {{
                color: #2c3e50;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """


def convert_html_to_pdf_macos(html_file: Path, pdf_file: Path) -> bool:
    """Convert HTML to PDF using macOS built-in tools."""
    try:
        # Try using cupsfilter (comes with macOS)
        subprocess.run(
            ['cupsfilter', str(html_file)],
            stdout=open(pdf_file, 'wb'),
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Try using textutil (macOS built-in)
        # First convert to RTF, then to PDF
        rtf_file = pdf_file.with_suffix('.rtf')
        subprocess.run(
            ['textutil', '-convert', 'rtf', '-output', str(rtf_file), str(html_file)],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ['textutil', '-convert', 'pdf', '-output', str(pdf_file), str(rtf_file)],
            check=True,
            capture_output=True
        )
        rtf_file.unlink()  # Clean up RTF file
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return False


def md_to_html_file(md_file: Path, html_file: Path) -> bool:
    """Convert markdown file to standalone HTML file."""
    try:
        # Read markdown content
        md_content = md_file.read_text(encoding='utf-8')

        # Convert to HTML
        title = md_file.stem.replace('_', ' ').title()
        html_content = markdown_to_html(md_content, title)

        # Write HTML file
        html_file.write_text(html_content, encoding='utf-8')

        print(f"✅ Converted: {md_file.name} → {html_file.name}")
        return True

    except Exception as e:
        print(f"❌ Error converting {md_file.name}: {e}")
        return False


def md_to_pdf(md_file: Path, pdf_file: Path) -> bool:
    """Convert markdown file to PDF (kept for backwards compatibility)."""
    # For now, just create HTML file with .html extension instead of .pdf
    html_file = pdf_file.with_suffix('.html')
    return md_to_html_file(md_file, html_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    success = md_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)
