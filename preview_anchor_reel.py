"""
Create a static reel-format image showing the anchor overlay
"""

from anchor_overlay import AnchorOverlaySystem
from PIL import Image, ImageDraw, ImageFont
import numpy as np

print('🎬 Creating reel-format preview with anchor overlay...')

# Create anchor system
anchor = AnchorOverlaySystem()

# Create a sample reel background (1080x1920)
reel_bg = Image.new('RGB', (1080, 1920), (30, 30, 50))

# Add sample headline text
draw = ImageDraw.Draw(reel_bg)
try:
    headline_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
except:
    headline_font = ImageFont.load_default()

# Draw headline at top
headline = "Breaking: Major News Story\nDeveloping Situation"
draw.text((40, 40), headline, font=headline_font, fill='white')

# Create anchor overlay
overlay_img, anchor_name = anchor.create_anchor_overlay(
    video_width=1080,
    video_height=1920,
    headline_height=180
)

# Composite overlay onto reel
# Position on LEFT SIDE, BELOW headline
x_position = 20  # Left side
y_position = 200  # Below headline (headline height ~180 + margin)

# Paste overlay (using alpha channel for transparency)
reel_bg.paste(overlay_img, (x_position, y_position), overlay_img)

# Save
output_path = '/Users/mahendrabahubali/Desktop/anchor_reel_preview.png'
reel_bg.save(output_path)

print(f'✅ Created reel preview: {output_path}')
print(f'👩‍💼 Anchor: {anchor_name}')
print(f'📐 Size: 1080x1920 (Instagram Reel format)')

# Open it
import os
os.system(f'open "{output_path}"')
