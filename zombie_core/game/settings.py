"""
All tunable numbers live here for rebalancing the game, such as
zombie speed, weapon damage, wave sizes, shop prices.
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
# --- Floor colors ---
GROUND_COLOR = (55, 60, 52)          
GROUND_COLOR_ALT = (50, 55, 47)     
GROUND_GROUT_COLOR = (35, 38, 33)  
GROUND_SEAM_COLOR = (30, 33, 28)    
GROUND_TILE_SIZE = 50
WOOD_COLOR = (150, 110, 60)

# --- Player ---
PLAYER_SIZE = 70
PLAYER_SPEED = 260
PLAYER_MAX_HEALTH = 100
# //to bring back when sprites are done
# PLAYER_FRAME_SIZE = 32     # size of one frame in assets/player/walk.png
# PLAYER_ANIM_SPEED = 0.12   # seconds per animation frame while moving

# Static character art (assets/character_designs/*.png) until walk cycles are ready
CHARACTER_DESIGN_PATHS = {
    "player": "character_designs/player.png",
    "walker": "character_designs/walker.png",
    "runner": "character_designs/runner.png",
    "brute": "character_designs/brute.png",
    "spitter": "character_designs/spitter.png",
    "boss": "character_designs/boss.png",
}

# --- Bullets ---
BULLET_RADIUS = 4
BULLET_SPEED = 750

# --- Waves ---
WAVE_BASE_COUNT = 4
WAVE_COUNT_STEP = 2
BREAK_DURATION = 60.0

# If the wave timer runs out and zombies are STILL alive, it's game
# over. Clearing all zombies before the timer ends always advances 
# to the next break regardless of time left.
WAVE_TIME_LIMIT_BASE = 55.0
WAVE_TIME_LIMIT_STEP = 7.0   

# --- Zombie types ---
# //to bring back when sprites are done
# ZOMBIE_FRAME_SIZE = 32     # size of one frame in assets/zombies/<type>/walk.png
# ZOMBIE_ANIM_SPEED = 0.15   # seconds per animation frame while moving
# Kill payouts tuned so a full clear through wave 4 stays under the
# machine gun (120); wave 5 + boss typically reaches it on the wave 6 break.
ZOMBIE_TYPES = {
    "walker": {
        "size": 44, "speed": 55, "health": 30, "contact_damage": 8,
        "color": (60, 110, 60), "currency": 3, "ranged": False,
        "hearing_range": 380,
    },
    "runner": {
        "size": 36, "speed": 95, "health": 16, "contact_damage": 6,
        "color": (170, 150, 60), "currency": 4, "ranged": False,
        "hearing_range": 450,
    },
    "brute": {
        "size": 62, "speed": 35, "health": 90, "contact_damage": 15,
        "color": (110, 60, 50), "currency": 5, "ranged": False,
        "hearing_range": 340,
    },
    "spitter": {
        "size": 40, "speed": 40, "health": 20, "contact_damage": 4,
        "color": (110, 150, 50), "currency": 4, "ranged": True,
        "hearing_range": 420,
    },
    "boss": {
        "size": 76, "speed": 42, "health": 260, "contact_damage": 22,
        "color": (150, 25, 25), "currency": 20, "ranged": False,
        "hearing_range": 500,
    },
}
BOSS_WAVE_INTERVAL = 5   # a boss spawns on wave 5 & 10

# Boss special attacks
BOSS_ABILITY_COOLDOWN = 5.0
BOSS_CHARGE_WINDUP = 0.85
BOSS_CHARGE_SPEED = 340
BOSS_CHARGE_DURATION = 0.55
BOSS_CHARGE_DAMAGE = 38
BOSS_CHARGE_MIN_DIST = 90
BOSS_CHARGE_MAX_DIST = 380
BOSS_SLAM_WINDUP = 1.05
BOSS_SLAM_RADIUS = 115
BOSS_SLAM_DAMAGE = 32
BOSS_SUMMON_WINDUP = 1.1
BOSS_SUMMON_COUNT = 5
BOSS_SUMMON_SPREAD = 55
BOSS_SUMMON_USES_PER_WAVE = (2, 3)   # each boss may summon this many times per wave

ZOMBIE_ATTACK_COOLDOWN = 0.7
ZOMBIE_ATTACK_RANGE = 6          # extra px beyond touching before contact registers
DIRECT_SIGHT_RANGE = 220         # zombies "see" the player at this range regardless of noise

SPITTER_RANGE_TILES = 4          # max distance spitter can shoot / telegraph length
SPITTER_PROJECTILE_TILES = 5     # projectile vanishes after this many tiles (if no hit)
SPITTER_RANGE = SPITTER_RANGE_TILES * GROUND_TILE_SIZE
SPITTER_PROJECTILE_MAX_DISTANCE = SPITTER_PROJECTILE_TILES * GROUND_TILE_SIZE
SPITTER_FIRE_COOLDOWN = 2.0
SPITTER_WINDUP = 0.65
SPITTER_PROJECTILE_SPEED = 220
SPITTER_PROJECTILE_DAMAGE = 6
SPIT_TELEGRAPH_COLOR = (186, 204, 132)   # pale puke-y green
SPIT_PROJECTILE_COLOR = (158, 188, 98)

HURT_FLASH_DURATION = 0.28
DEATH_POOF_DURATION = 0.5

# //to bring back when sprites are done
# Maps each internal zombie type key to its asset folder name
# ZOMBIE_ASSET_FOLDER = {
#     "walker": "normal",
#     "runner": "runner",
#     "brute": "brute",
#     "spitter": "spitter",
#     "boss": "boss",
# }

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
        "damage": 9, "fire_rate": 0.09, "max_ammo": 120,
        "pellets": 1, "spread": 0, "color": ORANGE, "noise_radius": 750,
    },
}

# The asset tree uses "machine_gun.png" mapped once here rather than
# renaming the id everywhere.
WEAPON_ASSET_FILE = {
    "pistol": "pistol.png",
    "rifle": "rifle.png",
    "shotgun": "shotgun.png",
    "machinegun": "machine_gun.png",
}

# --- Weapon rarity system ---
WEAPON_RARITY = {
    "pistol": "starter",
    "rifle": "common",
    "shotgun": "common",
    "machinegun": "rare",
}

# --- Weapon outline colors ---
WEAPON_COLORED_OUTLINES = True
WEAPON_OUTLINE_COLORS = {
    "pistol": (0x4C, 0xAF, 0x50),      # #4CAF50 green
    "rifle": (0x21, 0x96, 0xF3),       # #2196F3 blue
    "shotgun": (0x21, 0x96, 0xF3),     # #2196F3 blue (same tier as rifle)
    "machinegun": (0xB2, 0x4B, 0xF3),  # #B24BF3 purple
}

# --- God mode ---
GOD_MODE_KEY = pygame.K_BACKQUOTE   # the ` key toggles infinite health + ammo

# --- Win condition ---
WIN_AT_WAVE = 10   # clearing this wave's zombies ends the game as a win

# --- App-level states (menu / pause / game over / win) ---
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
NIGHT_TRANSITION_SPEED = 70

# --- Barricades ---
BARRICADE_MAX_HEALTH = 120
BARRICADE_SIZE = (46, 14)
BARRICADE_BUILD_COST_WOOD = 15
BARRICADE_BUILD_COST_METAL = 5
BARRICADE_REPAIR_COST_WOOD = 8
BARRICADE_REPAIR_AMOUNT = 40
BARRICADE_PLACE_DISTANCE = 50
BARRICADE_BLOCK_RADIUS = 200
BARRICADE_PLACEMENT_SPEED = 220
BARRICADE_PLACEMENT_MAX_RANGE = 170

# --- Pickups (spawned during the day) ---
PICKUP_RADIUS = 16
PICKUP_COLLECT_DISTANCE = 30
PICKUPS_PER_BREAK = (5, 8)

# Ammo pickups reuse the ammo/ rarity-tier icons rather than one icon per weapon.
AMMO_PICKUP_AMOUNTS = (5, 10, 15)
PICKUP_TYPES = {
    "wood": {"color": WOOD_COLOR, "amount_range": (18, 28)},
    "metal": {"color": (150, 155, 160), "amount_range": (7, 14)},
    "health": {"color": RED, "amount_range": (15, 25)},
    "ammo_pistol": {"color": (80, 200, 80)},
    "ammo_rifle": {"color": (80, 200, 80)},
    "ammo_shotgun": {"color": (80, 200, 80)},
    "ammo_machinegun": {"color": (170, 100, 220)},
}

# --- Shop ---
SHOP_ITEMS = [
    {"key": pygame.K_F1, "label": "Buy Rifle", "cost": 40, "kind": "weapon", "value": "rifle"},
    {"key": pygame.K_F2, "label": "Buy Shotgun", "cost": 60, "kind": "weapon", "value": "shotgun"},
    {"key": pygame.K_F3, "label": "Buy Machine Gun", "cost": 120, "kind": "weapon", "value": "machinegun"},
    {"key": pygame.K_F4, "label": "Ammo Refill (+20, current weapon)", "cost": 15, "kind": "ammo", "value": 20},
    {"key": pygame.K_F5, "label": "Health Pack (+30 HP)", "cost": 20, "kind": "health", "value": 30},
]

# --- On-screen notifications ---
TOAST_DURATION = 2.2

# --- Game states ---
STATE_BREAK = "break"
STATE_WAVE = "wave"
