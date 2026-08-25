https://opengameart.org/content/lpc-medieval-fantasy-character-sprites

https://opengameart.org/art-search-advanced?keys=character&title=&field_art_tags_tid_op=or&field_art_tags_tid=&name=&field_art_type_tid%5B0%5D=9&field_art_type_tid%5B1%5D=7273&sort_by=score&sort_order=DESC&items_per_page=24&Collection=&page=4

# 🧟 Zombie Survival

## ☐ Core Concept
- [ ] Survive escalating waves of zombies at night.
- [ ] Use daytime breaks to heal, loot, and shop before the next wave.

---

# ☐ Core Mechanics

### ✔ Player Movement & Combat ✔
- [x] WASD movement
- [x] Mouse aiming
- [x] Shoot toward mouse cursor
- [x] Zombie chase AI
- [x] Zombie health bars
- [x] Weapon damage system (different shots-to-kill)

### Weapons & Ammo
- [x] Current ammo counter
- [x] Color-coded ammo by weapon type
- [x] Multiple weapon system
- [ ] Weapon rarity system
- [ ] Rare weapon spawns

### ✔ Health ✔
- [x] Player health
- [x] Health packs
- [x] Healing during breaks

### ✔ Difficulty Scaling ✔
- [x] Increase zombie HP each wave
- [x] Increase zombie speed each wave
- [x] Increase zombie count

### ✔ Currency & Shop ✔
- [x] Currency drops from zombies
- [x] Shop between waves
- [x] Purchase weapons
- [x] Free pickups during breaks
  - [x] Health packs
  - [x] Ammo

### ✔ Day/Night Cycle ✔
- [x] Night starts zombie wave
- [x] Screen darkens at night
- [x] Wave ends when all of the zombies are dead
- [x] Screen brightens during break

---

# ☐ Extra Features

- [ ] Boss zombie in the final 5th wave
- [ ] Large boss currency reward
- [ ] Unique boss attack

---

# ✔ Kill Counter ✔

- [x] Total kills
- [x] Kills this wave
- [x] Zombies remaining counter

---

# ☐ HUD / On-Screen UI

### Always Visible
- [x] Player
- [x] Health bar
- [ ] Current weapon icon
- [x] Ammo count
- [x] Currency

### ✔ During Waves ✔
- [x] Zombies
- [x] Zombie HP bars (only when damaged)
- [x] Wave number
- [x] Zombies remaining

### During Breaks
- [x] Health packs
- [ ] Weapon spawns
- [x] Shop UI
- [x] Ammo pickups

---

# ☐ Zombie Types

Zombie types sprite : https://chatgpt.com/s/m_6a71ad8382dc819189ac1d0204b6f00c

## Walker
- [x] Sprite
- [ ] Walk animation - simnato na tel kako kje lichat walking directions-ot 25.08.2026 
  * [ ] Down
  * [ ] Down Left
  * [ ] Up
  * [ ] Up Left
  * [x] Left https://chatgpt.com/s/m_6a71ae13d2988191ad6747fef706835d https://chatgpt.com/s/m_6a71ad364b888191bd18d17d300a80d8
- [ ] Hurt frame
- [ ] Death frame

## Runner
- [x] Sprite
- [ ] Walk animation
  * [ ] Down
  * [ ] Down Left
  * [ ] Up
  * [ ] Up Left
  * [ ] Left
- [ ] Hurt frame
- [ ] Death frame

## Brute
- [x] Sprite
- [ ] Walk animation
  * [ ] Down
  * [ ] Down Left
  * [ ] Up
  * [ ] Up Left
  * [ ] Left
- [ ] Hurt frame
- [ ] Death frame

## Spitter
- [x] Sprite
- [ ] Walk animation
  * [ ] Down
  * [ ] Down Left
  * [ ] Up
  * [ ] Up Left
  * [ ] Left
- [ ] Attack animation
- [ ] Hurt frame
- [ ] Death frame

## Boss Zombie
- [x] Sprite
- [ ] Walk animation
  * [ ] Down
  * [ ] Down Left
  * [ ] Up
  * [ ] Up Left
  * [ ] Left
- [ ] Attack animation
- [ ] Hurt frame
- [ ] Death frame

---

# ☐ Animation Frames

### Every Normal Zombie
- [ ] Walk Down (6-9 frames)
- [ ] Walk Down Left (6-9 frame)
- [ ] Walk Up (6-9 frames)
- [ ] Walk Up Left (6-9 frames)
- [ ] Walk Left (6-9 frames)
- [ ] Flip Left for Right
- [ ] Hurt frame -> just red character when its hurt https://claude.ai/share/1bbfcbd7-5e33-4eb7-aef6-913dcc873094 <- posleden pasus 25.08.2026 09:42
- [ ] Death frame -> just a poof of white gas when dead

### Extra Animations
- [ ] Spitter attack
- [ ] Boss attack

---

# ☐ Weapons

## Common

### Pistol
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

---

## Uncommon

### Rifle
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

### Shotgun
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

---

## Rare

### Machine Gun
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

---

# ☐ Ammo Pickups

- [ ] Base ammo pickup sprite
- [ ] Green outline (Pistol) #4CAF50
- [ ] Blue outline (Rifle/Shotgun) #2196F3
- [ ] Purple outline (Machine Gun) #B24BF3

### Quantities
- [ ] x5
- [ ] x10
- [ ] x15

---

# ☐ Player

### Animations
- [ ] Idle Down
- [ ] Idle Up
- [ ] Idle Left
- [ ] Walk Down (3–4 frames)
- [ ] Walk Up (3–4 frames)
- [ ] Walk Left (3–4 frames)
- [ ] Flip Left for Right
- [ ] Hurt frame (or flash red in code)
- [ ] Death frame (optional)

---

# ☐ Polish

- [ ] Screen shake
- [ ] Sound effects
- [ ] Background music
- [ ] Game over screen
- [ ] Main menu
- [ ] Pause menu
- [ ] Restart button


# Needs improvement

- [x] Increase daytime (1min)
- [x] Enable the barriers to be positioned differently (use arrow keys for the position of the barrier | _ | and Enter to confirm the placement)
- [ ] Add a small number next to the ammo for the amount 
- [x] Small transition animation when it turn night and day 
- [x] Add a night duration: if the timer runs out and there are still zombies game over, if there are no zombies no matter the timer the game continues 
- [ ] After the 10th wave the game is over and the player wins
- [x] Show how many materials are needed for the barriers
- [x] Add a small health bar for them as well
- [x] How many materials are needed to repair a barier
- [x] Total zombie kill count
- [ ] For the buy phase -> we need a window UI because how do you buy ammo for different weapons? (key actions overlap)
- [ ] should we do the shop as a button that can be opened during the day? or should we keep it like this?, -> not added in the previous text (24.07.2026 9:44) like with a B key the shop window can open and with a click, ammo or weapon can be bought? since i plan to have like 5 different types of weapons
- [ ] lower day time when you are just starting (before the first wave it should be like 30s)
- [ ] night time should have like 5-10s per zombie depending on the type of zombie and how many hits it needs to be killed
