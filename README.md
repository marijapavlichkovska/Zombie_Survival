# Zombie Survival
A **2D pixel-art survival game** developed in Python using PyGame.

The goal is simple: survive increasingly difficult waves of zombies during the night, then use the daytime break to heal, collect resources, repair barricades, buy weapons and ammunition, and prepare for the next wave.

The game features multiple zombie types, different weapons and rarities, a day/night cycle, difficulty scaling, bosses, a shop system, barricades, and animated pixel-art characters.

## Game Overview
The game is structured around a day/night cycle. Each game consists of alternating daytime preparation phases and nighttime zombie waves.

### Day cycle
During the day, the player gets time to:
* Heal
* Collect free health packs
* Collect ammunition
* Repair and reposition barricades
* Purchase weapons
* Purchase ammunition
* Prepare for the upcoming wave

### Night cycle
At night, zombies spawn and begin attacking the player.
The player must:
* Move around the map
* Aim using the mouse
* Shoot incoming zombies
* Manage ammunition
* Use barricades strategically
* Survive until all zombies are defeated

If the night timer expires while zombies are still alive, the player loses. If all zombies are eliminated before the timer expires, the game continues to the next daytime phase.

A short transition animation plays when changing between day and night, and each wave becomes progressively harder.

**Objective:** Survive all **10 waves**, defeat the bosses, manage your resources, and make it through the final wave.

## Core Features

### Player & Combat
* WASD player movement
* Mouse aiming
* Shooting toward the mouse cursor
* Player health system
* Health packs
* Zombie chase AI
* Zombie health bars
* Different weapon damage values
* Different numbers of shots required to kill zombies

### Weapons
The game contains multiple weapons with different rarities and characteristics.
| Rarity | Weapon | Ammunition |
|---------|-------------|---------|
| 🟢 Common | Pistol | Green #4CAF50 |
| 🔵 Uncommon | Rifle | Blue #2196F3 |
| 🔵 Uncommon | Shotgun | Blue #2196F3 |
| 🟣 Rare | Machine Gun | Purple #B24BF3 |

Each weapon has its own ammunition type and color-coded ammunition pickups.

Ammo pickups are available in different quantities:
* x5
* x10
* x15

## Zombie Types
The game contains several zombie types with different characteristics.
* **Walker** - Standard zombie with normal speed, health, and basic chase behavior.
* **Runner** - Fast zombie with high movement speed but lower health.
* **Brute** - Slow, high-health zombie that requires more shots to defeat.
* **Spitter** - Ranged zombie that keeps its distance and attacks the player from afar.
  * **Ranged Attack** - Attacks the player from a distance.
* **Boss Zombie** - Powerful zombie appearing on Wave 5 and 10, with high health, unique attacks, and a large currency reward.
  * **Charge** - Rushes toward the player, requiring them to dodge.
  * **Ground Slam** - Deals area-of-effect damage around the boss.
  * **Summon** - Summons additional zombies to increase the pressure on the player.

## Difficulty Scaling
Zombie difficulty increases as the player progresses through the waves.

The game increases:
* Zombie health
* Zombie movement speed
* Number of zombies
* Overall wave difficulty

The amount of time available during a night is also influenced by the number and type of zombies.

Different zombie types receive different time allowances depending on their difficulty and how many hits they require to defeat.

## Barricades
Barricades can be used to slow down or control zombies.

The player can:
* Position barricades differently
* Move the barricade position using the arrow keys
* Confirm placement with Enter
* See the materials required to build a barricade
* See the barricade's health
* Repair damaged barricade using materials

This allows the player to create defensive positions before a wave begins.

## Currency & Shop
Zombies drop currency when defeated.

Currency can be used during the daytime preparation phase to purchase:
* Weapons
* Ammunition

The shop uses a dedicated UI window to make purchasing different ammunition types easier.

## Kill Counter & HUD
The game tracks the player's progress through several HUD elements.

### Always Visible
* Player
* Health bar
* Current weapon
* Ammunition
* Currency

### During Waves
* Wave number
* Zombies remaining
* Zombie health bars when damaged
* Kills this wave
* Total kills

### During Daytime
* Health packs
* Ammunition pickups
* Shop interface
* Barricade information

## Pixel Art & Animation
The game uses custom **2D pixel-art sprites and animations**.

### Zombie Animations
Normal zombies use directional walking animations:
* Down
* Down Left
* Down Right
* Up
* Up Left
* Up Right
* Left
* Right

### Additional Animations
* Hurt animation
* Death animation
* Spitter attack animation
* Boss attack animations

The player uses a smaller animation set:
* Idle Down
* Idle Up
* Idle Left
* Walk Down
* Walk Up
* Walk Left
* Right-facing animations through flipping
* Hurt effect

## Menus & UI
The game includes:
* Main Menu
* Pause Menu
* Game Over Screen
* Victory Screen
* Shop UI
* HUD
* Wave information
* Kill counters
* Resource indicators

## Controls
| Key / Input | Action |
|---------|----------|
| W | Move Up |
| A | Move Left |
| S | Move Down |
| D | Move Right |
| Mouse | Aim / Interact with UI |
| Left Mouse Button | Shoot at night / Interact with shop and barricade UI during the day |
| 1 / 2 / 3 / 4 | Switch weapon if owned |
| ` | Toggle God Mode (testing purposes) |
| B | Start placing a barricade during the day |
| Arrow Keys | Move barricade preview |
| Space | Rotate barricade |
| Enter | Confirm barricade placement |
| R | Repair nearest barricade in range during the day |
| Esc | Cancel barricade placement / Pause game |

## Technologies
The game is developed using:
* **Python** - main programming language
* **PyGame** - 2D game development framework
* **2D Pixel Art** - characters, weapons, items and UI assets
* **Sprite Animation** - character movement and combat animations
* **GitHub** - version control and project management

## Development Status
The core gameplay systems are implemented, including:
* Player movement
* Shooting and aiming
* Zombie AI
* Zombie health
* Multiple weapons
* Weapon rarity
* Ammunition system
* Health system
* Currency
* Shop
* Day/night cycle
* Wave progression
* Difficulty scaling
* Boss waves
* Kill counters
* Barricades
* Main menu
* Pause menu
* Game over screen
* Victory condition after Wave 10

### Remaining Work
* Runner walking animations
* Spitter walking animations
* Spitter attack animation
* Boss walking animations
* Boss attack animation
* Player animations
* Final animation polishing
