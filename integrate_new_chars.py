#!/usr/bin/env python3
"""Replace SVG symbols in index.html with new AI-generated characters."""

import re

HTML = '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/index.html'
CHARS = {
    'baobao':  '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/char_baobao.svg',
    'hargow':  '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/char_hargow.svg',
    'siumai':  '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/char_siumai.svg',
    'eggtart': '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/char_eggtart.svg',
    'charsiu': '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/char_charsiu.svg',
    'jin':     '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots/char_jin.svg',
}

with open(HTML, 'r') as f:
    html = f.read()

print(f'Original HTML size: {len(html)}')

for key, svg_path in CHARS.items():
    with open(svg_path, 'r') as f:
        new_svg = f.read().strip()
    
    # Escape for template literal: backticks need \`, $ need \$, \ need \\
    # But we can use String.raw trick or just escape what needs escaping
    escaped = new_svg.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    
    # Find old SVG block: svg: `<svg...>` followed eventually by },
    # The old SVG blocks end with </svg>`
    # Pattern: svg: \`<svg...<\/svg>\`
    pattern = rf'(// ── .+? ─+\.\.\.\.\s+{key}: \{{\s+svg: `)<svg[^`]*(</svg>`)'
    
    # Simpler approach: find "svg: \`" after the key comment, until the matching </svg>`
    # Build a regex that matches from "svg: \`" to "</svg>`"
    
    # Find position of key in file
    key_pattern = rf'\/\/ ── .+? ─+\.\.\.\.\s+{key}: \{{'
    m = re.search(key_pattern, html)
    if not m:
        print(f'  {key}: key pattern not found!')
        continue
    
    start = m.start()
    # Find svg: \` after the key
    svg_start_m = re.search(rf'{key}: \{{\s+svg: `', html[start:])
    if not svg_start_m:
        print(f'  {key}: svg start not found!')
        continue
    
    actual_start = start + svg_start_m.end() - 1  # back up to include the opening backtick
    # Actually: the pattern ends at the backtick before <svg
    # The svg: ` starts at position svg_start_m.start() + len(f'{key}: {{')
    # Let's find the actual svg: ` position
    svg_start_backtick = start + svg_start_m.end() - 1  # this is the opening backtick
    # Actually let me re-read the match
    # The regex was: (// ── .+? ─+\.\.\.\.\s+{key}: \{{\s+svg: `)
    # So the group ends right before the <svg tag, at the opening backtick
    # The opening backtick is at position: start + svg_start_m.end()
    open_backtick = start + svg_start_m.end()
    
    # Find the closing </svg>`
    close_m = re.search(r'</svg>`', html[open_backtick:])
    if not close_m:
        print(f'  {key}: closing </svg>` not found!')
        continue
    
    close_pos = open_backtick + close_m.end() - 1  # position of the closing backtick
    
    old_block = html[open_backtick-1:close_pos+1]  # include both backticks
    print(f'  {key}: old block {len(old_block)} chars, new SVG {len(escaped)} chars')
    
    new_block = '`' + escaped + '`'
    html = html[:open_backtick-1] + new_block + html[close_pos+1:]

print(f'New HTML size: {len(html)}')

with open(HTML, 'w') as f:
    f.write(html)

print('Done!')

# Quick sanity check - verify key symbols are present
for key in CHARS:
    if key in html:
        print(f'  {key}: present in HTML ✓')
    else:
        print(f'  {key}: MISSING from HTML!')
