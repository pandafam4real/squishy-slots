#!/usr/bin/env python3
"""Convert AI-generated PNG characters to inline SVG for Squishy Slots."""

import base64, io, os, json
from PIL import Image

MEDIA = '/Users/jaykayoldmba/.openclaw/media/tool-image-generation'
OUT = '/Users/jaykayoldmba/.openclaw/workspace/squishy-slots'

# Map: symbol key -> filename
CHARS = {
    'baobao':  'baobao_cartoon_v2---827f27ca-edfa-4e7e-9f2e-bea66839c245.png',
    'hargow':  'hargow_cartoon_v2---8ff0dc8c-628a-4c5f-b460-1701ed1023c8.png',
    'siumai':  'siumai_cartoon_v2---d716269c-2080-4b05-b391-94bce83e2bca.png',
    'eggtart': 'eggtart_cartoon_v2---19333b5c-fdd4-4f3e-8a61-91e71bad752a.png',
    'charsiu': 'charsiu_cartoon_v2---ca39f7fe-6f8d-46fa-af41-1b7735cd65c1.png',
    'jin':     'jin_cosmic_ultra---44bb901a-6b31-43f1-ae85-0ca495862122.png',
}

def process_char(key, fname):
    path = f'{MEDIA}/{fname}'
    img = Image.open(path).convert('RGBA')
    w, h = img.size
    print(f'  {key}: {w}x{h}')

    # Crop to tight bounding box of non-white content
    # Scan for any pixel that's not mostly white (threshold 240)
    bg = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    diff = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    
    pix = img.load()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            # If pixel is noticeably different from white
            if not (r > 220 and g > 220 and b > 220):
                if a > 10:
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
    
    # Add 4px padding
    pad = 4
    min_x = max(0, min_x - pad)
    min_y = max(0, min_y - pad)
    max_x = min(w, max_x + pad)
    max_y = min(h, max_y + pad)
    
    cropped = img.crop((min_x, min_y, max_x, max_y))
    cw, ch = cropped.size
    print(f'    Cropped: {cw}x{ch}, bbox=({min_x},{min_y})-({max_x},{max_y})')
    
    # Resize to 56x56 max (leaving 8px padding in 64x64 cell)
    max_dim = max(cw, ch)
    scale = 52.0 / max_dim
    new_w = int(cw * scale)
    new_h = int(ch * scale)
    cropped = cropped.resize((new_w, new_h), Image.LANCZOS)
    
    # Center in 64x64
    offset_x = (64 - new_w) // 2
    offset_y = (64 - new_h) // 2
    
    # Build 64x64 transparent canvas
    canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    canvas.paste(cropped, (offset_x, offset_y))
    
    # Save PNG to repo
    png_path = f'{OUT}/char_{key}.png'
    canvas.save(png_path, 'PNG')
    print(f'    Saved PNG: {png_path}')
    
    # Convert to base64
    buf = io.BytesIO()
    canvas.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    
    # Build SVG
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 64 64" width="64" height="64">'
        f'<image width="64" height="64" xlink:href="data:image/png;base64,{b64}"/>'
        f'</svg>'
    )
    
    svg_path = f'{OUT}/char_{key}.svg'
    with open(svg_path, 'w') as f:
        f.write(svg)
    print(f'    Saved SVG: {svg_path}')
    
    return svg

print('Processing characters...')
svgs = {}
for key, fname in CHARS.items():
    print(f'Processing {key}...')
    svgs[key] = process_char(key, fname)

print('\nDone! SVG data:')
for k, v in svgs.items():
    print(f'{k}: {len(v)} chars')
