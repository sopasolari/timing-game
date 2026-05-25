from ursina import *
import random

app = Ursina()

ground = Entity(model='plane', color=color.dark_gray, scale=(10, 1, 1000), position=(0, -1, 0))
player = Entity(model='cube', color=color.orange, scale=(1, 2, 1), position=(0, 0, 0), collider='box')

obstacles = []

# --- GAME STATE & LANES (ΟΙ 3 ΛΩΡΙΔΕΣ) ---
lanes = [-3, 0, 3] # Left, Center, Right X-coordinates
current_lane = 1   # Start in the Center lane (index 1)

# Switches to prevent getting stuck
is_jumping = False
is_crouching = False


def spawn_obstacle():
    lane_x = random.choice(lanes) # Spawn in one of the 3 lanes randomly
    obs = Entity(model='cube', color=color.red, scale=(1.5, 2, 1.5), position=(lane_x, 0, player.z + 60), collider='box')
    obstacles.append(obs)
    invoke(spawn_obstacle, delay=1.5)

spawn_obstacle()


def update():
    # 1. Run forward
    player.z += 10 * time.dt
    
    # 2. Smoothly snap to the selected lane
    player.x = lerp(player.x, lanes[current_lane], time.dt * 10)
    
    # 3. Collision (Game Over)
    hit_info = player.intersects()
    if hit_info.hit:
        print("CRASH! GAME OVER!")
        application.quit()
        
    # 4. Clean up old obstacles
    for obs in obstacles:
        if obs.z < player.z - 5:
            destroy(obs)
            obstacles.remove(obs)
    
    # 5. Fixed Camera (No more dizziness!)
    camera.z = player.z - 15
    camera.y = 5
    camera.x = 0 # Lock camera to the center of the track
    camera.rotation_x = 15 # Look slightly down


# --- RESET FUNCTIONS FOR SAFE JUMP/CROUCH ---
def reset_jump():
    global is_jumping
    is_jumping = False

def reset_crouch():
    global is_crouching
    is_crouching = False


def input(key):
    global current_lane, is_jumping, is_crouching
    
    # --- LANE CHANGING ---
    if key == 'd' or key == 'right arrow':
        if current_lane < 2: # Move right if not already in the rightmost lane
            current_lane += 1
            
    if key == 'a' or key == 'left arrow':
        if current_lane > 0: # Move left if not already in the leftmost lane
            current_lane -= 1
            
    # --- JUMPING ---
    if key == 'space':
        if not is_jumping and not is_crouching:
            is_jumping = True
            player.animate_y(2, duration=0.3, curve=curve.out_sine)
            player.animate_y(0, duration=0.3, delay=0.3, curve=curve.in_sine)
            invoke(reset_jump, delay=0.65) # Reset safely after animation ends
            
    # --- CROUCHING ---
    if key == 'down arrow':
        if not is_crouching and not is_jumping:
            is_crouching = True
            player.animate_scale((1, 1, 1), duration=0.1)
            player.animate_y(-0.5, duration=0.1)
            
            player.animate_scale((1, 2, 1), duration=0.1, delay=1)
            player.animate_y(0, duration=0.1, delay=1)
            invoke(reset_crouch, delay=1.15) # Reset safely after animation ends

app.run()