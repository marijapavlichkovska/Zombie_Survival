# 🧟 Zombie Survival

## ☐ Core Concept
- [ ] Survive escalating waves of zombies at night.
- [ ] Use daytime breaks to heal, loot, and shop before the next wave.

---

# ☐ Core Mechanics

### Player Movement & Combat
- [x] WASD movement
- [x] Mouse aiming
- [x] Shoot toward mouse cursor
- [x] Zombie chase AI
- [x] Zombie health bars
- [ ] Weapon damage system (different shots-to-kill)

### Weapons & Ammo
- [ ] Current ammo counter
- [ ] Color-coded ammo by weapon type
- [ ] Multiple weapon system
- [ ] Weapon rarity system
- [ ] Rare weapon spawns

### Health
- [x] Player health
- [x] Health packs
- [ ] Healing during breaks

### Difficulty Scaling
- [ ] Increase zombie HP each wave
- [ ] Increase zombie speed each wave
- [ ] Increase zombie contact damage
- [x] Increase zombie count

### Currency & Shop
- [ ] Currency drops from zombies
- [x] Shop between waves
- [x] Purchase weapons
- [ ] Purchase upgrades
- [x] Free pickups during breaks
  - [x] Health packs
  - [x] Ammo

### Day/Night Cycle
- [x] Night starts zombie wave
- [x] Screen darkens at night
- [ ] Dawn ends wave
- [x] Screen brightens during break

---

# ☐ Extra Features

- [ ] Boss zombie every 5 waves
- [ ] Blood particle effects
- [ ] Large boss currency reward
- [ ] Unique boss attack

---

# ☐ Kill Counter

- [ ] Total kills
- [x] Kills this wave
- [x] Zombies remaining counter

---

# ☐ HUD / On-Screen UI

### Always Visible
- [x] Player
- [x] Health bar
- [ ] Current weapon icon
- [ ] Ammo count
- [ ] Wave number
- [ ] Currency
- [ ] Zombies remaining

### During Waves
- [ ] Zombies
- [ ] Zombie HP bars (only when damaged)

### During Breaks
- [ ] Health packs
- [ ] Weapon spawns
- [ ] Shop UI
- [ ] Ammo pickups

---

# ☐ Zombie Types

## Walker
- [ ] Sprite
- [ ] Walk animation
- [ ] Hurt frame
- [ ] Death frame

## Runner
- [ ] Sprite
- [ ] Walk animation
- [ ] Hurt frame
- [ ] Death frame

## Brute
- [ ] Sprite
- [ ] Walk animation
- [ ] Hurt frame
- [ ] Death frame

## Spitter
- [ ] Sprite
- [ ] Walk animation
- [ ] Attack animation
- [ ] Hurt frame
- [ ] Death frame

## Boss Zombie
- [ ] Sprite
- [ ] Walk animation
- [ ] Attack animation
- [ ] Hurt frame
- [ ] Death frame

---

# ☐ Animation Frames

### Every Normal Zombie
- [ ] Walk Down (3–4 frames)
- [ ] Walk Up (3–4 frames)
- [ ] Walk Left (3–4 frames)
- [ ] Flip Left for Right
- [ ] Hurt frame
- [ ] Death frame

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

### SMG
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

---

## Uncommon

### Shotgun
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Pellet sprite
- [ ] Muzzle flash

### Rifle
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

---

## Rare

### Sniper
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

### Machine Gun
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Bullet sprite
- [ ] Muzzle flash

---

## Legendary

### Special Weapon
- [ ] Choose weapon
- [ ] Weapon icon
- [ ] Held sprite (optional)
- [ ] Projectile sprite
- [ ] Muzzle flash
- [ ] Special effect

---

# ☐ Ammo Pickups

- [ ] Base ammo pickup sprite
- [ ] Green outline (Pistol/SMG)
- [ ] Blue outline (Rifle)
- [ ] Purple outline (Sniper/Machine Gun)
- [ ] Gold outline (Legendary)

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
- [ ] Use arrow keys for movement during zombie attacks
- [ ] Add a small number next to the ammo for the amount 
- [x] Small transition animation when it turn night and day 
- [x] Add a night duration: if the timer runs out and there are still zombies game over, if there are no zombies no matter the timer the game continues 
- [ ] After the 5th wave the game is over and the player wins
- [x] Show how many materials are needed for the barriers
- [x] Add a small health bar for them as well
- [x] How many materials are needed to repair a barier
- [x] Total zombie kill count
- [ ] For the buy phase -> we need a window UI because how do you buy ammo for different weapons? (key actions overlap)

raise the shop a bit more up to fill in the gap, 
should we do the shop as a button that can be opened during the day? or should we keep it like this?, like with a B key the shop window can open and with a click, ammo or weapon can be bought? since i plan to have like 5 different types of weapons
lower day time when you are just starting (before the first wave it should be like 30s)
night time should have like 5-10s per zombie depending on the type of zombie and how many hits it needs to be killed
