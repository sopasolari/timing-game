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
level_text = Text(text='Level: 1', position=(-0.70, 0.45), origin=(-0.5, 0), scale=2, color=color.cyan)


is_jumping = False
is_crouching = False


def spawn_obstacle():
    lane_x = random.choice(lanes)
    
    spawn_distance = 60 + (current_speed * 2)
    obs = Entity(model='cube', color=color.red, scale=(1.5, 2, 1.5), position=(lane_x, 0, player.z + spawn_distance), collider='box')
    obstacles.append(obs)
    
    spawn_delay = 15.0 / current_speed
    invoke(spawn_obstacle, delay=spawn_delay)

spawn_obstacle()


def update():
    global play_time, current_level, current_speed
    
    # 1. UPDATE TIME & PROGRESSION
    play_time += time.dt
    timer_text.text = f'Time: {round(play_time, 1)}'
    
    new_level = int(play_time / 10) + 1
    if new_level > current_level:
        current_level = new_level
        current_speed += 2.0 
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


# --- RESET FLAGS ---
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
        if current_lane < 4: 
            current_lane += 1
            
    if key == 'a' or key == 'left arrow':
        if current_lane > 0: 
            current_lane -= 1
            
    # --- JUMPING ---
    if key == 'space':
        if not is_jumping and not is_crouching:
            is_jumping = True
            
            # 1. Άλμα προς τα πάνω
            player.animate_y(2, duration=0.3, curve=curve.out_sine)
            
            # 2. Λειτουργία για κάθοδο (τρέχει ΜΕΤΑ από 0.3s)
            def jump_down():
                player.animate_y(0, duration=0.3, curve=curve.in_sine)
            invoke(jump_down, delay=0.3)
            
            # 3. Ξεκλείδωμα πλήκτρου
            invoke(reset_jump, delay=0.65)
            
    # --- CROUCHING ---
    if key == 'down arrow':
        if not is_crouching and not is_jumping:
            is_crouching = True
            
            # 1. Σκύψιμο προς τα κάτω
            player.animate_scale((1, 1, 1), duration=0.1)
            player.animate_y(-0.5, duration=0.1)
            
            # 2. Λειτουργία για σήκωμα (τρέχει ΜΕΤΑ από 1s)
            def stand_up():
                player.animate_scale((1, 2, 1), duration=0.1)
                player.animate_y(0, duration=0.1)
            invoke(stand_up, delay=1.0)
            
            # 3. Ξεκλείδωμα πλήκτρου
            invoke(reset_crouch, delay=1.15)

app.run()