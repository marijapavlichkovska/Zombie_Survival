"""
Generates placeholder art into the exact asset folder structure shown
in the project tree, so the game is immediately runnable and every
file path already matches what your real art will replace. Drop your
actual PNGs in over these (same filenames) and nothing else needs to
change -- the game loads by path, not by "is this a placeholder".

Run this once: `python generate_placeholders.py`

Folder layout (matches your screenshot):
    assets/materials/{wood,metal,currency}.png       -- 24x24 icons
    assets/weapons/{pistol,rifle,shotgun,machine_gun}.png  -- 24x24 icons
    assets/ammo/{common,uncommon,rare}.png            -- 24x24 rarity icons
    assets/player/walk.png                            -- 32x32 x4 cols x3 rows (down/up/left)
    assets/zombies/<type>/walk.png                    -- same layout, one per type
"""

from PIL import Image, ImageDraw
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FRAME_SIZE = 32
FRAMES_PER_ROW = 4
DIRECTIONS = ["down", "up", "left"]  # "right" is generated in-code by flipping "left"


def _draw_character(draw, cx, cy, body_color, outline_color, facing, bob, swing):
    body_w, body_h = 14, 18
    cy += bob
    top, left = cy - body_h // 2, cx - body_w // 2

    draw.ellipse([left, top, left + body_w, top + body_h], fill=body_color, outline=outline_color, width=2)
    head_r = 6
    draw.ellipse([cx - head_r, top - head_r + 4, cx + head_r, top + head_r + 4], fill=body_color, outline=outline_color, width=2)

    if facing == "down":
        draw.ellipse([cx - 2, top + head_r + 2, cx + 2, top + head_r + 6], fill=outline_color)
    elif facing == "up":
        draw.ellipse([cx - 2, top - head_r + 2, cx + 2, top - head_r + 6], fill=outline_color)
    elif facing == "left":
        draw.ellipse([left - 2, cy - 2, left + 2, cy + 2], fill=outline_color)

    arm_w, arm_h = 3, 8
    draw.rectangle([left - 2, cy - arm_h // 2 + swing, left - 2 + arm_w, cy + arm_h // 2 + swing], fill=outline_color)
    draw.rectangle([left + body_w - 1, cy - arm_h // 2 - swing, left + body_w - 1 + arm_w, cy + arm_h // 2 - swing], fill=outline_color)


def make_walk_sheet(path, body_color, outline_color):
    sheet = Image.new("RGBA", (FRAME_SIZE * FRAMES_PER_ROW, FRAME_SIZE * len(DIRECTIONS)), (0, 0, 0, 0))
    bob_pattern = [0, -1, 0, 1]
    swing_pattern = [-2, 0, 2, 0]

    for row, direction in enumerate(DIRECTIONS):
        for frame in range(FRAMES_PER_ROW):
            frame_img = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(frame_img)
            _draw_character(draw, FRAME_SIZE // 2, FRAME_SIZE // 2 + 2, body_color, outline_color,
                             direction, bob_pattern[frame], swing_pattern[frame])
            sheet.paste(frame_img, (frame * FRAME_SIZE, row * FRAME_SIZE), frame_img)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    print(f"Saved {path}")


def make_icon(path, color, outline, shape="rect", size=24):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = 4
    if shape == "rect":
        draw.rectangle([pad, pad, size - pad, size - pad], fill=color, outline=outline, width=2)
    elif shape == "circle":
        draw.ellipse([pad, pad, size - pad, size - pad], fill=color, outline=outline, width=2)
    elif shape == "gun":
        draw.rectangle([2, size * 0.4, size - 6, size * 0.6], fill=color, outline=outline, width=2)
        draw.rectangle([size - 10, 2, size - 2, size * 0.4], fill=color, outline=outline, width=2)
    elif shape == "outline_square":
        draw.rectangle([pad, pad, size - pad, size - pad], outline=color, width=3)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Saved {path}")


def make_medpack_icon(path, size=24):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, size - 2, size - 2], fill=(235, 235, 235, 255), outline=(180, 30, 30, 255), width=2)
    cx, cy = size // 2, size // 2
    draw.rectangle([cx - 2, 5, cx + 2, size - 5], fill=(200, 30, 30, 255))
    draw.rectangle([5, cy - 2, size - 5, cy + 2], fill=(200, 30, 30, 255))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Saved {path}")


def make_shop_button_icon(path, size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, size - 2, size - 2], fill=(60, 130, 90, 255), outline=(20, 50, 30, 255), width=3)
    # simple shopping-bag silhouette
    bag_w, bag_h = size * 0.42, size * 0.38
    left, top = size / 2 - bag_w / 2, size / 2 - bag_h / 2 + 4
    draw.rectangle([left, top, left + bag_w, top + bag_h], fill=(255, 220, 120, 255), outline=(90, 60, 10, 255), width=2)
    handle_r = bag_w * 0.28
    draw.arc([size / 2 - handle_r, top - handle_r * 1.3, size / 2 + handle_r, top + handle_r * 0.7],
             start=180, end=360, fill=(90, 60, 10, 255), width=2)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Saved {path}")


if __name__ == "__main__":
    # --- materials ---
    make_icon(os.path.join(BASE, "assets/materials/wood.png"), (150, 110, 60, 255), (70, 45, 20, 255), "rect")
    make_icon(os.path.join(BASE, "assets/materials/metal.png"), (170, 175, 180, 255), (90, 95, 100, 255), "rect")
    make_icon(os.path.join(BASE, "assets/materials/currency.png"), (230, 200, 60, 255), (140, 110, 20, 255), "circle")
    make_medpack_icon(os.path.join(BASE, "assets/materials/medpack.png"))

    # --- shop button ---
    make_shop_button_icon(os.path.join(BASE, "assets/shop.png"))

    # --- weapons ---
    make_icon(os.path.join(BASE, "assets/weapons/pistol.png"), (230, 200, 60, 255), (30, 30, 30, 255), "gun")
    make_icon(os.path.join(BASE, "assets/weapons/rifle.png"), (70, 130, 220, 255), (30, 30, 30, 255), "gun")
    make_icon(os.path.join(BASE, "assets/weapons/shotgun.png"), (150, 90, 200, 255), (30, 30, 30, 255), "gun")
    make_icon(os.path.join(BASE, "assets/weapons/machine_gun.png"), (230, 140, 50, 255), (30, 30, 30, 255), "gun")

    # --- ammo rarity tiers ---
    make_icon(os.path.join(BASE, "assets/ammo/common.png"), (80, 200, 80, 255), (20, 60, 20, 255), "outline_square")
    make_icon(os.path.join(BASE, "assets/ammo/uncommon.png"), (80, 140, 220, 255), (20, 40, 60, 255), "outline_square")
    make_icon(os.path.join(BASE, "assets/ammo/rare.png"), (170, 100, 220, 255), (60, 20, 80, 255), "outline_square")

    # --- player ---
    make_walk_sheet(os.path.join(BASE, "assets/player/walk.png"), (70, 130, 180, 255), (20, 40, 60, 255))

    # --- zombies (folder names match the project tree: normal/runner/brute/spitter/boss) ---
    make_walk_sheet(os.path.join(BASE, "assets/zombies/normal/walk.png"), (60, 110, 60, 255), (30, 45, 25, 255))
    make_walk_sheet(os.path.join(BASE, "assets/zombies/runner/walk.png"), (170, 150, 60, 255), (75, 65, 25, 255))
    make_walk_sheet(os.path.join(BASE, "assets/zombies/brute/walk.png"), (110, 60, 50, 255), (55, 25, 20, 255))
    make_walk_sheet(os.path.join(BASE, "assets/zombies/spitter/walk.png"), (110, 150, 50, 255), (50, 70, 20, 255))
    make_walk_sheet(os.path.join(BASE, "assets/zombies/boss/walk.png"), (150, 25, 25, 255), (60, 5, 5, 255))

    print("\nAll placeholder assets generated. Replace any file above with your own art (same filename) at any time.")
