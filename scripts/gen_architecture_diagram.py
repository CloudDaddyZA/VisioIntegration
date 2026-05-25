"""Generate the architecture diagram for README.md"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create high-resolution image
W, H = 1100, 780
img = Image.new('RGBA', (W, H), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Fonts
try:
    font_title = ImageFont.truetype('segoeui.ttf', 28)
    font_subtitle = ImageFont.truetype('segoeuib.ttf', 20)
    font_body = ImageFont.truetype('segoeui.ttf', 16)
    font_small = ImageFont.truetype('segoeui.ttf', 13)
except Exception:
    font_title = ImageFont.load_default()
    font_subtitle = font_title
    font_body = font_title
    font_small = font_title

# Colors
blue_bg = (235, 243, 255)
blue_border = (100, 149, 237)
green_bg = (235, 255, 240)
green_border = (60, 140, 60)
card_bg = (255, 255, 255)
card_border = (80, 130, 80)
yellow_bg = (255, 248, 220)
yellow_border = (200, 170, 50)
purple_bg = (245, 240, 255)
purple_border = (150, 120, 200)
text_dark = (30, 30, 30)
text_blue = (40, 80, 160)
text_green = (30, 80, 30)
text_gray = (100, 100, 100)

# --- Top Section: Streamlit App ---
draw.rounded_rectangle([30, 20, W-30, 280], radius=12, fill=blue_bg, outline=blue_border, width=2)
draw.text((W//2, 42), "Streamlit App (UI)", fill=text_blue, font=font_title, anchor="mt")

# AI Agent box
draw.rounded_rectangle([70, 80, 290, 250], radius=8, fill=card_bg, outline=blue_border, width=1)
draw.ellipse([155, 95, 205, 130], fill=(100, 149, 237), outline=blue_border)
draw.text((180, 112), ":)", fill=(255, 255, 255), font=font_body, anchor="mm")
draw.text((180, 150), "AI Agent", fill=text_dark, font=font_subtitle, anchor="mm")
draw.text((180, 175), "(OpenAI)", fill=text_gray, font=font_body, anchor="mm")

# MCP Client box
draw.rounded_rectangle([360, 80, 580, 250], radius=8, fill=yellow_bg, outline=yellow_border, width=1)
draw.rounded_rectangle([445, 95, 495, 130], radius=4, fill=(40, 40, 80))
draw.text((470, 112), ">_", fill=(200, 255, 200), font=font_body, anchor="mm")
draw.text((470, 150), "MCP Client", fill=text_dark, font=font_subtitle, anchor="mm")
draw.text((470, 175), "(stdio)", fill=text_gray, font=font_body, anchor="mm")

# Diagram Preview box
draw.rounded_rectangle([650, 80, 870, 250], radius=8, fill=purple_bg, outline=purple_border, width=1)
draw.rectangle([735, 95, 785, 130], fill=(240, 240, 255), outline=purple_border)
draw.line([(735, 105), (785, 105)], fill=purple_border, width=1)
draw.text((760, 150), "Diagram Preview", fill=text_dark, font=font_subtitle, anchor="mm")
draw.text((760, 175), "(SVG renderer)", fill=text_gray, font=font_body, anchor="mm")

# Arrows between top components
draw.line([(290, 165), (360, 165)], fill=text_dark, width=2)
draw.polygon([(355, 160), (362, 165), (355, 170)], fill=text_dark)
draw.line([(580, 165), (650, 165)], fill=text_dark, width=2)
draw.polygon([(645, 160), (652, 165), (645, 170)], fill=text_dark)

# --- Arrow between sections ---
draw.line([(W//2, 280), (W//2, 335)], fill=text_dark, width=2)
draw.polygon([(W//2-5, 330), (W//2, 340), (W//2+5, 330)], fill=text_dark)
draw.text((W//2 + 15, 295), "stdio (JSON-RPC)", fill=text_gray, font=font_body, anchor="lt")

# --- Bottom Section: MCP Server ---
draw.rounded_rectangle([30, 345, W-30, 755], radius=12, fill=green_bg, outline=green_border, width=2)
draw.text((W//2, 365), "MCP Server (FastMCP)", fill=text_green, font=font_title, anchor="mt")

# Grid of 9 modules (3x3)
modules = [
    ["Diagram", "State"],
    ["Layout", "Engine"],
    ["Reference", "Architectures (\u00d712)"],
    ["WAF", "Validator"],
    ["CAF", "Validator"],
    ["Azure Catalog", "(151 shapes, 124 SVG)"],
    ["Visio COM", "Engine"],
    ["Draw.io", "Engine"],
    ["Architecture Catalog", "(206 entries)"],
]

col_w = 310
row_h = 115
start_x = 60
start_y = 400

icon_colors = [
    (60, 120, 60),    # Diagram State
    (60, 140, 100),   # Layout Engine
    (40, 80, 160),    # Ref Arch
    (80, 130, 60),    # WAF
    (80, 130, 60),    # CAF
    (0, 120, 212),    # Azure Catalog
    (180, 50, 50),    # Visio COM
    (200, 80, 40),    # Draw.io
    (60, 100, 60),    # Arch Catalog
]

for i, lines in enumerate(modules):
    col = i % 3
    row = i // 3
    x = start_x + col * (col_w + 20)
    y = start_y + row * (row_h + 12)

    draw.rounded_rectangle([x, y, x + col_w, y + row_h], radius=8, fill=card_bg, outline=card_border, width=1)

    # Icon
    ix = x + 15
    iy = y + 15
    draw.rounded_rectangle([ix, iy, ix + 28, iy + 28], radius=5, fill=icon_colors[i])

    # Text
    draw.text((x + 55, y + 20), lines[0], fill=text_dark, font=font_subtitle, anchor="lt")
    draw.text((x + 55, y + 46), lines[1], fill=text_gray, font=font_body, anchor="lt")

# Save
os.makedirs("docs", exist_ok=True)
out_path = os.path.join("docs", "architecture.png")
img.save(out_path, "PNG")
print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
