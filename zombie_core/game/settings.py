"""
All tunable numbers live here. If you want to rebalance the game
(zombie speed, weapon damage, wave sizes, shop prices...), this is
the only file you should need to touch.
"""

import pygame

# --- Window ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
FPS = 60
TITLE = "Zombie Survival"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 40, 40)
GREEN = (60, 200, 60)
YELLOW = (230, 200, 60)
GREY = (80, 80, 80)
LIGHT_GREY = (170, 170, 170)
BLUE = (70, 130, 220)
PURPLE = (150, 90, 200)
ORANGE = (230, 140, 50)
GROUND_COLOR = (55, 60, 52)          # base tile color
GROUND_COLOR_ALT = (50, 55, 47)      # slightly darker alternate tile (checkerboard)
GROUND_GROUT_COLOR = (35, 38, 33)    # line between tiles
GROUND_SEAM_COLOR = (30, 33, 28)     # thicker panel seam every few tiles
GROUND_TILE_SIZE = 50
WOOD_COLOR = (150, 110, 60)

# --- Player ---
PLAYER_SIZE = 28
PLAYER_SPEED = 260
PLAYER_MAX_HEALTH = 100
PLAYER_FRAME_SIZE = 32     # size of one frame in assets/player/walk.png
PLAYER_ANIM_SPEED = 0.12   # seconds per animation frame while moving

# --- Bullets ---
BULLET_RADIUS = 4
BULLET_SPEED = 750

# --- Waves ---
WAVE_BASE_COUNT = 4
WAVE_COUNT_STEP = 2
BREAK_DURATION = 60.0        # a full minute now that there's pickups + shop + barricade building to do

# If the wave timer runs out and zombies are STILL alive, it's game
# over (you got overrun). Clearing all zombies before the timer ends
# always advances to the next break regardless of time left.
WAVE_TIME_LIMIT_BASE = 55.0
WAVE_TIME_LIMIT_STEP = 7.0   # scales closer to how fast zombie count grows per wave, so later waves don't get proportionally tighter

# --- Zombie types ---
# Speeds tuned to feel manageable -- see main_v2 changelog notes if
# you want to compare against the earlier (faster) tuning.
# Currency values roughly doubled from the original tuning so weapon
# purchases (especially the 120g machine gun) feel reachable within a
# reasonable number of waves instead of a very long grind.
ZOMBIE_FRAME_SIZE = 32     # size of one frame in assets/zombies/<type>/walk.png
ZOMBIE_ANIM_SPEED = 0.15   # seconds per animation frame while moving
ZOMBIE_TYPES = {
    "walker": {
        "size": 26, "speed": 55, "health": 30, "contact_damage": 8,
        "color": (60, 110, 60), "currency": 10, "ranged": False,
        "hearing_range": 380,
    },
    "runner": {
        "size": 20, "speed": 95, "health": 16, "contact_damage": 6,
        "color": (170, 150, 60), "currency": 14, "ranged": False,
        "hearing_range": 450,
    },
    "brute": {
        "size": 36, "speed": 35, "health": 90, "contact_damage": 15,
        "color": (110, 60, 50), "currency": 22, "ranged": False,
        "hearing_range": 340,
    },
    "spitter": {
        "size": 24, "speed": 40, "health": 20, "contact_damage": 4,
        "color": (110, 150, 50), "currency": 18, "ranged": True,
        "hearing_range": 420,
    },
    "boss": {
        # appears every BOSS_WAVE_INTERVAL waves (see wave.py) -- much
        # tankier and hits harder than anything else, and drops a big
        # currency reward to match the risk of fighting it
        "size": 44, "speed": 42, "health": 260, "contact_damage": 22,
        "color": (150, 25, 25), "currency": 80, "ranged": False,
        "hearing_range": 500,
    },
}
BOSS_WAVE_INTERVAL = 5   # a boss spawns on wave 5, 10, 15, ...

ZOMBIE_ATTACK_COOLDOWN = 0.7
ZOMBIE_ATTACK_RANGE = 6          # extra px beyond touching before contact registers
DIRECT_SIGHT_RANGE = 220         # zombies "see" the player at this range regardless of noise

SPITTER_RANGE = 350
SPITTER_FIRE_COOLDOWN = 2.0
SPITTER_PROJECTILE_SPEED = 220
SPITTER_PROJECTILE_DAMAGE = 6

# Maps each internal zombie type key to its asset folder name --
# kept separate because the project's asset tree uses "normal" for
# what the code calls "walker" internally (renaming the internal key
# everywhere would be a much bigger, riskier change for no real
# benefit over just mapping it once here).
ZOMBIE_ASSET_FOLDER = {
    "walker": "normal",
    "runner": "runner",
    "brute": "brute",
    "spitter": "spitter",
    "boss": "boss",
}

# --- Weapons ---
WEAPONS = {
    "pistol": {
        "damage": 6, "fire_rate": 0.30, "max_ammo": 60,
        "pellets": 1, "spread": 0, "color": YELLOW, "noise_radius": 380,
    },
    "rifle": {
        "damage": 10, "fire_rate": 0.22, "max_ammo": 50,
        "pellets": 1, "spread": 0, "color": BLUE, "noise_radius": 480,
    },
    "shotgun": {
        "damage": 6, "fire_rate": 0.7, "max_ammo": 24,
        "pellets": 4, "spread": 14, "color": PURPLE, "noise_radius": 560,
    },
    "machinegun": {
        # rare and expensive: not much per-shot damage, but a very
        # fast fire rate gives it the highest sustained DPS of any
        # weapon -- and the biggest noise radius by far, since a
        # machine gun realistically should be the loudest thing you
        # can carry. A big ammo pool so it can actually sustain that
        # fire rate for a few seconds before needing a refill.
        "damage": 9, "fire_rate": 0.09, "max_ammo": 120,
        "pellets": 1, "spread": 0, "color": ORANGE, "noise_radius": 750,
    },
}

# The asset tree uses "machine_gun.png" (with underscore) while the
# internal id is "machinegun" -- mapped once here rather than
# renaming the id everywhere.
WEAPON_ASSET_FILE = {
    "pistol": "pistol.png",
    "rifle": "rifle.png",
    "shotgun": "shotgun.png",
    "machinegun": "machine_gun.png",
}

# Rarity grouping: rifle and shotgun are both "common", machine gun
# is "rare" (pistol is the free starter, not part of the rarity system).
WEAPON_RARITY = {
    "pistol": "starter",
    "rifle": "common",
    "shotgun": "common",
    "machinegun": "rare",
}

# --- Weapon outline colors ---
# Set WEAPON_COLORED_OUTLINES = False to turn this off entirely and
# fall back to the plain white/grey outline scheme instead (used on
# the bottom weapon-bar slots in hud.py, and on the aim-direction
# line drawn from the player in player.py).
WEAPON_COLORED_OUTLINES = True
WEAPON_OUTLINE_COLORS = {
    "pistol": (0x4C, 0xAF, 0x50),      # #4CAF50 green
    "rifle": (0x21, 0x96, 0xF3),       # #2196F3 blue
    "shotgun": (0x21, 0x96, 0xF3),     # #2196F3 blue (same tier as rifle)
    "machinegun": (0xB2, 0x4B, 0xF3),  # #B24BF3 purple
}

# --- God mode ---
GOD_MODE_KEY = pygame.K_BACKQUOTE   # the ` key -- toggles infinite health + ammo

# --- Win condition ---
WIN_AT_WAVE = 10   # clearing this wave's zombies ends the game as a win

# --- App-level states (menu / pause / game over / win), separate
# from the day-night STATE_BREAK / STATE_WAVE below ---
APP_STATE_MENU = "app_menu"
APP_STATE_PLAYING = "app_playing"
APP_STATE_PAUSED = "app_paused"
APP_STATE_GAMEOVER = "app_gameover"
APP_STATE_WIN = "app_win"

# --- Shop button (click to open/close the shop panel) ---
SHOP_BUTTON_SIZE = (64, 64)
# center-right of the screen
SHOP_BUTTON_POS = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 - 32)

# --- Noise system ---
WALK_NOISE_RADIUS = 90
WALK_NOISE_INTERVAL = 0.4      # emit a footstep noise event this often while moving
NOISE_DECAY_TIME = 1.2         # how long a noise event stays "active"

# --- Day/night transition ---
NIGHT_ALPHA_MAX = 140
NIGHT_TRANSITION_SPEED = 70   # alpha units per second -- ~2s for a full day<->night fade

# --- Barricades ---
BARRICADE_MAX_HEALTH = 120
BARRICADE_SIZE = (46, 14)
BARRICADE_BUILD_COST_WOOD = 15
BARRICADE_BUILD_COST_METAL = 5
BARRICADE_REPAIR_COST_WOOD = 8
BARRICADE_REPAIR_AMOUNT = 40
BARRICADE_PLACE_DISTANCE = 50     # initial distance in front of the player when starting placement
BARRICADE_BLOCK_RADIUS = 200      # zombies within this range treat it as a potential obstacle
BARRICADE_PLACEMENT_SPEED = 220   # px/sec the ghost preview moves while held with arrow keys
BARRICADE_PLACEMENT_MAX_RANGE = 170  # how far from the player you're allowed to place one

# --- Pickups (spawned during the day/break phase) ---
# Each pickup type: display color, and the range of amount it grants
# when collected. Player walks over one to collect it automatically.
PICKUP_RADIUS = 16   # bigger than before so ground drops are easy to spot
PICKUP_COLLECT_DISTANCE = 30     # how close the player needs to be to auto-collect
PICKUPS_PER_BREAK = (5, 8)       # (min, max) pickups spawned at the start of each break

# Ammo pickups reuse the ammo/ rarity-tier icons rather than one icon
# per weapon: rifle and shotgun ammo are both "common", machine gun
# ammo is "rare" (matches the shop's weapon rarity -- see
# WEAPON_OUTLINE_COLORS below for the same grouping applied to colors).
PICKUP_TYPES = {
    "wood": {"color": WOOD_COLOR, "amount_range": (18, 28)},
    "metal": {"color": (150, 155, 160), "amount_range": (7, 14)},
    "health": {"color": RED, "amount_range": (15, 25)},
    "ammo_pistol": {"color": (80, 200, 80), "amount_range": (10, 20)},
    "ammo_rifle": {"color": (80, 200, 80), "amount_range": (8, 16)},
    "ammo_shotgun": {"color": (80, 200, 80), "amount_range": (4, 10)},
    "ammo_machinegun": {"color": (170, 100, 220), "amount_range": (10, 20)},
}

# --- Shop ---
# kind "weapon" -> value is weapon id to unlock
# kind "ammo"   -> value is amount of ammo added to CURRENT weapon
# kind "health" -> value is HP restored
#
# Kept separate from the 1/2/3 weapon-switch keys so you can freely
# switch weapons (even during the day) to pick which one an ammo
# refill applies to. The shop panel is also fully mouse-clickable
# (see game/shop.py get_layout()) as an alternative to any keybind.
SHOP_ITEMS = [
    {"key": pygame.K_F1, "label": "Buy Rifle", "cost": 40, "kind": "weapon", "value": "rifle"},
    {"key": pygame.K_F2, "label": "Buy Shotgun", "cost": 60, "kind": "weapon", "value": "shotgun"},
    {"key": pygame.K_F3, "label": "Buy Machine Gun", "cost": 120, "kind": "weapon", "value": "machinegun"},
    {"key": pygame.K_F4, "label": "Ammo Refill (+20, current weapon)", "cost": 15, "kind": "ammo", "value": 20},
    {"key": pygame.K_F5, "label": "Health Pack (+30 HP)", "cost": 20, "kind": "health", "value": 30},
]

# --- On-screen notifications ("toasts") ---
TOAST_DURATION = 2.2

# --- Game states ---
STATE_BREAK = "break"
STATE_WAVE = "wave"
