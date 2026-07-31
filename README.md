# Zombie_Survival

## Core Concept
You survive escalating waves of zombies at night, and use the daytime breaks to heal, loot, and shop for better gear before the next wave hits.

## Core Mechanics
* WASD movement — player walks left/right/forward/backward. Zombies walk toward the player during a wave (simple chase AI, move toward player position each frame).
* Mouse aiming — player aims and shoots toward the cursor. Each zombie has a health bar; shots-to-kill depends on weapon damage vs. zombie HP (e.g., 5 pistol shots vs. 3 rifle shots to kill a base zombie).
* Ammo — current ammo count shown on screen at all times, color-coded to match weapon type.
* Multiple weapons — rarer weapon spawns during breaks deal more damage / kill zombies faster.
* Health packs — spawn during breaks, heal the player if they took damage during the last wave.
* Increasing difficulty — scales on two axes so it doesn't feel like just a bullet-sponge grind:
* Zombie stats scale up per wave (contact damage, speed, HP) — e.g. wave 1 = -5 HP on hit, wave 2 = -10 HP, etc.
* Zombie count also increases per wave — more enemies, not just tougher ones.
* Currency + Shop between rounds — killing zombies drops currency. Basic items (health packs, common ammo) are free pickups during breaks; weapons and upgrades cost currency in the shop. This adds a resource-management decision layer during breaks instead of just "walk around and grab things."
Day/Night cycle — night falls → wave starts (screen darkens, tension); dawn breaks → wave ends → break/shop phase (screen brightens, calm/safe).

## Extras
* Boss zombie — appears at set wave intervals (e.g. every 5th wave), much higher HP, unique attack pattern, drops significantly more currency.
* Blood particles — small fading squares/circles on hit, simple velocity + alpha fade, no extra art needed.
* Fog — omitted (adds visual clutter without gameplay payoff; day/night overlay already covers atmosphere).

## Kill Counter
* Total kills (per run) — resets each playthrough, shown on HUD or pause/game-over screen.
* Kills this wave — used to calculate "zombies remaining" (remaining = wave total − kills this wave).

## On-Screen Elements

### Always visible
* Player
* Health bar
* Current weapon indicator (small icon, bottom-right corner)
* Ammo count (color-coded to weapon type)
* Wave number (e.g. "Wave 3")
* Zombies remaining (during waves)
* Currency total

### During zombie waves
* Zombies (with HP bar shown only when damaged, not at full health)
* Zombies remaining counter

### During breaks
* Health packs (free pickup)
* Weapon spawns (rare, weighted by rarity tier)
* Shop UI (buy weapons/upgrades with currency)
* Ammo pickups — color-coded outline by weapon type, spawn in stackable amounts (x5 / x10 / x15)

## Zombie Types To Draw
* Walker (base zombie) - Standard enemy, bulk of every wave; Plain, slightly decayed look, torn clothes; Baseline HP/speed/damage
* Runner (fast zombie) - Rushes the player, punishes standing still; Leaner build, tattered/missing clothing, maybe leaning forward pose; Low HP, high speed, moderate damage
* Brute (tank zombie) - Slow but dangerous, needs sustained fire; Bulkier silhouette, bigger arms/shoulders, darker/rotting color palette; High HP, low speed, high contact damage
* Spitter (ranged zombie) - Adds ranged threat, forces movement instead of just standing and shooting; Bloated torso/head, maybe a distinct color (sickly green) to signal "ranged"; Low HP, throws projectile, low melee damage
* Boss Zombie - Special wave-ending encounter - Noticeably larger scale, unique color scheme (e.g. deep red/black), maybe a visual "tell" for an attack animation; Very high HP, unique attack pattern, big currency drop

### Frames needed per zombie type (based on the sheet you showed me):
* Walk cycle: 6-9 frames × 5 directions (down/down left/up/up left/left — flip left for right)
* Hurt/death frame: 1-2 frames
* Spitter needs an attack/throw frame; Boss needs its own attack animation

### Weapons To Draw

Group by rarity tier so spawn weighting is easy to implement later.

#### Common
* Pistol - Starting weapon, low damage, high ammo availability
* SMG - Fast fire rate, low damage per shot
#### Uncommon
* Shotgun - High damage up close, short range
* Rifle - Balanced damage/fire rate, better than pistol per shot
##### Rare
* Machine Gun - High sustained damage, high ammo consumption

### Per weapon, you'll need:
* Small icon sprite (for HUD "current weapon" indicator and shop listing)
* Held/equipped sprite if you want the player to visibly hold it (optional polish)
* Muzzle flash (1-2 frames, can be shared/reused across similar weapon types)
* Bullet/projectile sprite (can share one bullet sprite across pistol/rifle/SMG, and a distinct one for shotgun pellets or sniper rounds if you want visual variety)

### Ammo Pickups to Draw
Base ammo pickup shape, recolored/outlined per weapon category:
* Green outline — pistol/SMG ammo
* Blue outline — rifle ammo
* Purple outline — sniper/machine gun ammo
* Gold outline — legendary weapon ammo (if applicable)

Each spawn in stackable quantities (x5 / x10 / x15) — this can just be a text label over the same sprite, no need for separate art per quantity.

Suggested Player Sprite Frame List
* Idle (down-facing minimum, ideally 1 per direction)
* Walk cycle: 6-9 frames × 5 directions (down/down left/up/up left/left flip for right)
* Hurt frame (flash red via code)

#### Optional: death frame for game-over screen
