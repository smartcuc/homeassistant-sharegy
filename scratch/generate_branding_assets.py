"""
Generates high-resolution PNG and SVG brand assets for Stripe Dashboard branding.
"""

import os
from PIL import Image, ImageDraw, ImageFont

public_dir = r"c:\Users\Public\Dev\eswes\frontend\public"

# 1. ICON (512x512 PNG)
def generate_icon():
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background with gradient simulation
    radius = 110
    # Gradient from Indigo #4f46e5 to Violet #7c3aed to Amber #f59e0b
    for y in range(size):
        r = int(79 + (124 - 79) * (y / size))
        g = int(70 + (58 - 70) * (y / size))
        b = int(229 + (237 - 229) * (y / size))
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Mask for smooth rounded corners
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(16, 16), (size - 16, size - 16)], radius=radius, fill=255)
    img.putalpha(mask)

    # Draw sharp, dynamic Lightning Bolt Symbol
    # Polygon coordinates centered
    bolt_draw = ImageDraw.Draw(img)
    bolt_points = [
        (280, 75),
        (165, 275),
        (255, 275),
        (215, 435),
        (355, 225),
        (265, 225),
        (310, 75)
    ]
    # Subtle drop shadow
    shadow_points = [(x + 4, y + 6) for (x, y) in bolt_points]
    bolt_draw.polygon(shadow_points, fill=(30, 27, 75, 120))
    bolt_draw.polygon(bolt_points, fill=(255, 255, 255, 255))

    icon_path = os.path.join(public_dir, "sharegy-stripe-icon.png")
    img.save(icon_path, "PNG")
    print(f"Generated {icon_path}")

# 2. HORIZONTAL LOGO (1024x256 PNG)
def generate_logo():
    width = 1024
    height = 256
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw left icon badge (190x190)
    badge_size = 190
    badge_x = 35
    badge_y = 33
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(badge)

    for y in range(badge_size):
        r = int(79 + (124 - 79) * (y / badge_size))
        g = int(70 + (58 - 70) * (y / badge_size))
        b = int(229 + (237 - 229) * (y / badge_size))
        b_draw.line([(0, y), (badge_size, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (badge_size, badge_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(4, 4), (badge_size - 4, badge_size - 4)], radius=42, fill=255)
    badge.putalpha(mask)

    # Lightning on badge
    scale = badge_size / 512.0
    bolt_points = [
        (int(280 * scale), int(75 * scale)),
        (int(165 * scale), int(275 * scale)),
        (int(255 * scale), int(275 * scale)),
        (int(215 * scale), int(435 * scale)),
        (int(355 * scale), int(225 * scale)),
        (int(265 * scale), int(225 * scale)),
        (int(310 * scale), int(75 * scale))
    ]
    b_draw.polygon(bolt_points, fill=(255, 255, 255, 255))
    img.paste(badge, (badge_x, badge_y), badge)

    # Draw text "Sharegy"
    try:
        font = ImageFont.truetype("arialbd.ttf", 108)
        sub_font = ImageFont.truetype("arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    draw.text((255, 60), "Sharegy", fill=(15, 23, 42, 255), font=font)
    draw.text((260, 168), "HOME ENERGY OS & SHARING", fill=(99, 102, 241, 255), font=sub_font)

    logo_path = os.path.join(public_dir, "sharegy-stripe-logo.png")
    img.save(logo_path, "PNG")
    print(f"Generated {logo_path}")

# 3. SVG VERSIONS
def generate_svgs():
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="shGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f46e5"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.25"/>
    </filter>
  </defs>
  <rect x="16" y="16" width="480" height="480" rx="110" fill="url(#shGradient)"/>
  <polygon points="280,75 165,275 255,275 215,435 355,225 265,225 310,75" fill="#ffffff" filter="url(#shadow)"/>
</svg>"""

    svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" width="1024" height="256">
  <defs>
    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f46e5"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
  </defs>
  <!-- Icon Badge -->
  <rect x="35" y="33" width="190" height="190" rx="42" fill="url(#logoGrad)"/>
  <polygon points="139,61 96,135 130,135 115,195 167,117 133,117 150,61" fill="#ffffff"/>
  
  <!-- Text -->
  <text x="255" y="145" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="105" font-weight="900" fill="#0f172a" letter-spacing="-1.5">Sharegy</text>
  <text x="260" y="195" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="22" font-weight="700" fill="#6366f1" letter-spacing="3.5">HOME ENERGY OS &amp; SHARING</text>
</svg>"""

    with open(os.path.join(public_dir, "sharegy-stripe-icon.svg"), "w", encoding="utf-8") as f:
        f.write(svg_icon)
    with open(os.path.join(public_dir, "sharegy-stripe-logo.svg"), "w", encoding="utf-8") as f:
        f.write(svg_logo)
    print("Generated SVGs")

if __name__ == "__main__":
    generate_icon()
    generate_logo()
    generate_svgs()
