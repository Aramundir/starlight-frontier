# 🌌 Starlight Frontier

**Starlight Frontier** is a 2D space combat game built with Python and Pygame. You command a player ship in a vast starfield arena, battling increasingly difficult waves of enemy ships using physics-driven controls, maneuvering thrusters, and projectile-based combat.

---

## 🚀 Features

- Dynamic space combat with computer-controlled enemies
- Physics-based ship movement and momentum
- Multiple ship classes: Scout, Fighter, Heavy Fighter
- Difficulty scaling across levels
- Simple HUD with game state (win/lose) handling
- Procedural starfield background
- Smooth 60 FPS game loop

---

## 🎮 Controls

| Key          | Action                         |
|--------------|--------------------------------|
| `W`          | Accelerate forward             |
| `S`          | Accelerate backward            |
| `A`          | Turn left                      |
| `D`          | Turn right                     |
| `Q`          | Lateral thrust left            |
| `E`          | Lateral thrust right           |
| `X`          | Brake (slow down)              |
| `SPACE`      | Fire projectiles               |
| `R`          | Restart game after win/loss    |

---

## 🧠 Game Mechanics

### Ship Classes
- **Scout** – Fast and nimble, low hull points.
- **Fighter** – Balanced speed and firepower.
- **Heavy Fighter** – Slow but durable with strong firepower.

Each ship uses thrusters for acceleration and lateral movement, adhering to Newtonian motion.

### AI Enemies
- Enemies pursue the player and align their facing angle before firing.
- AI adapts to player movement and attempts flanking via lateral thrusts.

### Projectiles
- Spawn from hardpoints with forward velocity
- Use vector math for motion and collisions

---

## 🧩 Code Structure

```
.
├── game_loop.py        # Main game loop and input handling
├── game_engine.py      # Handles physics, HUD, spawning, and rendering
├── entities.py         # Defines Ship and Projectile classes
```

### `game_loop.py`
- Sets up the game window and Pygame environment
- Handles the main update/draw loop
- Implements win/loss/restart logic and user input

### `game_engine.py`
- Defines helper systems:
  - `Physics`: Collision detection
  - `Spawner`: Initializes player and enemy ships
  - `ScreenPainter`: Background and UI screens
  - `HUD`: Draws info overlays

### `entities.py`
- Contains the core `Ship` and `Projectile` classes
- Implements movement physics, rotation, AI behavior, and firing logic

---

## 📦 Requirements

- Python 3.12
- Pygame 2.6.1

---

## ▶️ Running the Game

To run **Starlight Frontier** in an isolated environment, follow these steps:

1. **Create a virtual environment** (first time only):
	
	```bash
	python -m venv venv
	```

2. **Activate the virtual environment**:

	- On macOS/Linux:
	
		```bash
		source venv/bin/activate
		```

	- On Windows (CMD):
	
		```bash
		venv\Scripts\activate
		```

3. **Install dependencies from `requirements.txt`**:

	```bash
	pip install -r requirements.txt
	```

4. **Run the game**:

	```bash
	python game_loop.py
	```

To deactivate the environment later:

```bash
deactivate
```

---

## 🛠️ Roadmap / Future Features

- Audio effects (shooting, thrusters)
- More ship classes and weapons
- Velocity-based damage for collisions and projectiles
- Better physics (Rotation inertia, braking according ship thruster direction)
- Better and varied ship behaviour (Passive, patrolling, traveling)
- Space Stations, neutral and allied ships, missions
- Larger universe, without "arena-based" fights like now
- Enhanced HUD with aiming lines, ammo, etc.
- Save/load system

---

## 📄 License

This project is currently under development and not yet licensed.

---

## 💬 Credits

Developed by Aramundir  
Built with Python and Pygame

---

## 🛰️ Screenshots

_I will add a few gameplay images here once available:_
