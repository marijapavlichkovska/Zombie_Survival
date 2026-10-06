import random

from game.settings import (
    WAVE_BASE_COUNT, WAVE_COUNT_STEP, SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS_WAVE_INTERVAL,
)
from game.zombie import Zombie
from game.boss_zombie import BossZombie


def _spawn_edge_position():
    edge = random.choice(["top", "bottom", "left", "right"])
    if edge == "top":
        return random.uniform(0, SCREEN_WIDTH), -30
    elif edge == "bottom":
        return random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
    elif edge == "left":
        return -30, random.uniform(0, SCREEN_HEIGHT)
    else:
        return SCREEN_WIDTH + 30, random.uniform(0, SCREEN_HEIGHT)


def spawn_wave(wave_number):
    """Returns a list of new Zombie instances for this wave. Early
    waves are mostly walkers so the player isn't overwhelmed with
    variety before they've had a chance to buy anything. 
    
    Every BOSS_WAVE_INTERVAL waves, a boss spawns in addition to the 
    normal count -- it has its own fixed stat multiplier rather than 
    scaling with wave number, since its base stats are already tuned 
    to be a standalone threat."""
    count = WAVE_BASE_COUNT + (wave_number - 1) * WAVE_COUNT_STEP
    health_multiplier = 1.0 + (wave_number - 1) * 0.15
    speed_multiplier = 1.0 + (wave_number - 1) * 0.04

    if wave_number == 1:
        type_pool = ["walker"]
    elif wave_number == 2:
        type_pool = ["walker", "walker", "runner"]
    else:
        type_pool = ["walker", "walker", "runner", "brute", "spitter"]

    zombies = []
    for _ in range(count):
        x, y = _spawn_edge_position()
        ztype = random.choice(type_pool)
        zombies.append(Zombie(x, y, ztype, health_multiplier, speed_multiplier))

    if wave_number % BOSS_WAVE_INTERVAL == 0:
        x, y = SCREEN_WIDTH / 2, -40 
        zombies.append(BossZombie(x, y, health_multiplier, speed_multiplier))

    return zombies
