from ursina import *
import random

app = Ursina()

# --- ENVIRONMENT ---
ground = Entity(model='plane', color=color.dark_gray, scale=(15, 1, 2000), position=(0, -1, 0))
player = Entity(model='cube', color=color.orange, scale=(1, 2, 1), position=(0, 0, 0), collider='box')

obstacles = []

# --- GAME STATE & LANES ---
lanes = [-6, -3, 0, 3, 6]
current_lane = 2

# --- PROGRESSION SYSTEM (Time, Level, Speed) ---
play_time = 0.0
current_level = 1
current_speed = 10.0 # Base speed

# --- UI ELEMENTS ---
timer_text = Text(text='Time: 0.0', position=(0, 0.45), origin=(0,0), scale=2, color=color.yellow)
level_text = Text(text='Level: 1', position=(-0.85, 0.45), origin=(-0.5,0), scale=2, color=color.cyan)

is_jumping = False
is_crouching = False


def spawn_obstacle():
    lane_x = random.choice(lanes)
    
    # Spawn obstacle further ahead as speed increases so player has time to react
    spawn_distance = 60 + (current_speed * 2)
    obs = Entity(model='cube', color=color.red, scale=(1.5, 2, 1.5), position=(lane_x, 0, player.z + spawn_distance), collider='box')
    obstacles.append(obs)
    
    # Calculate delay based on speed (faster speed = faster spawning)
    spawn_delay = 15.0 / current_speed
    invoke(spawn_obstacle, delay=spawn_delay)

spawn_obstacle()


def update():
    global play_time, current_level, current_speed
    
    # 1. UPDATE TIME & PROGRESSION
    play_time += time.dt
    timer_text.text = f'Time: {round(play_time, 1)}'
    
    # Calculate level (increases every 10 seconds now!)
    new_level = int(play_time / 10) + 1
    if new_level > current_level:
        current_level = new_level
        current_speed += 2.0 # Increase speed by 2 every level
        level_text.text = f'Level: {current_level}'
    
    # 2. RUNNING & LANE CHANGING
    player.z += current_speed * time.dt
    player.x = lerp(player.x, lanes[current_lane], time.dt * 10)
    
    # 3. COLLISION
    hit_info = player.intersects()
    if hit_info.hit:
        print(f"CRASH! GAME OVER! Reached Level {current_level} and survived for {round(play_time, 1)} seconds.")
        application.quit()
        
    # 4. CLEANUP
    for obs in obstacles:
        if obs.z < player.z - 5:
            destroy(obs)
            obstacles.remove(obs)
    
    # 5. CAMERA SETUP 
    camera.z = player.z - 22
    camera.y = 8
    camera.x = 0
    camera.rotation_x = 18


def reset_jump():
    global is_jumping
    is_jumping = False

def reset_crouch():
    global is_crouching
    is_crouching = False


def input(key):
    global current_lane, is_jumping, is_crouching
    
    if key == 'd' or key == 'right arrow':
        if current_lane < 4: 
            current_lane += 1
            
    if key == 'a' or key == 'left arrow':
        if current_lane > 0: 
            current_lane -= 1
            
    if key == 'space':
        if not is_jumping and not is_crouching:
            is_jumping = True
            player.animate_y(2, duration=0.3, curve=curve.out_sine)
            player.animate_y(0, duration=0.3, delay=0.3, curve=curve.in_sine)
            invoke(reset_jump, delay=0.65)
            
    if key == 'down arrow':
        if not is_crouching and not is_jumping:
            is_crouching = True
            player.animate_scale((1, 1, 1), duration=0.1)
            player.animate_y(-0.5, duration=0.1)
            
            player.animate_scale((1, 2, 1), duration=0.1, delay=1)
            player.animate_y(0, duration=0.1, delay=1)
            invoke(reset_crouch, delay=1.15)

app.run()