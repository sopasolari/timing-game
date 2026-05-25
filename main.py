from ursina import *
import random

app = Ursina()

# --- GAME STATE ---
game_active = False 
has_crashed = False  
lanes = [-6, -3, 0, 3, 6]
current_lane = 2
play_time = 0.0
current_level = 1
current_speed = 10.0
is_jumping = False
is_crouching = False

# --- INVINCIBILITY SYSTEM ---
is_invincible = False
invincibility_timer = 0.0

# Spawner memory for pseudo-randomness
last_spawned_lane = None
consecutive_spawns = 0

# --- ENVIRONMENT ---
ground = Entity(model='plane', color=color.dark_gray, scale=(15, 1, 2000), position=(0, -1, 0))
player = Entity(model='cube', color=color.orange, scale=(1, 2, 1), position=(0, 0, 0), collider='box')
obstacles = []
stars = [] 

# --- UI ELEMENTS ---
timer_text = Text(text='Time: 0.0', position=(0, 0.45), origin=(0,0), scale=2, color=color.yellow, enabled=False)
level_text = Text(text='Level: 1', position=(-0.70, 0.45), origin=(-0.5,0), scale=2, color=color.cyan, enabled=False)
invincible_text = Text(text='INVINCIBLE! 5.0s', position=(0, 0.35), origin=(0,0), scale=3, color=color.gold, enabled=False)

# ==========================================
# --- MENUS SETUP ---
# ==========================================
start_menu = Entity(parent=camera.ui)
pause_menu = Entity(parent=camera.ui, enabled=False)
game_over_menu = Entity(parent=camera.ui, enabled=False)

# --- MENU FUNCTIONS ---
def go_to_main_menu():
    global game_active, has_crashed, is_invincible
    game_active = False
    has_crashed = False
    is_invincible = False
    player.color = color.orange
    
    start_menu.enabled = True
    pause_menu.enabled = False
    game_over_menu.enabled = False
    timer_text.enabled = False
    level_text.enabled = False
    invincible_text.enabled = False
    
    for obs in obstacles:
        destroy(obs)
    obstacles.clear()
    
    for s in stars:
        destroy(s)
    stars.clear()

def start_new_game():
    global game_active, play_time, current_level, current_speed, current_lane, has_crashed
    global last_spawned_lane, consecutive_spawns, is_invincible
    
    play_time = 0.0
    current_level = 1
    current_speed = 10.0
    current_lane = 2
    has_crashed = False
    is_invincible = False
    player.color = color.orange
    last_spawned_lane = None
    consecutive_spawns = 0
    player.position = (0, 0, 0)
    
    for obs in obstacles:
        destroy(obs)
    obstacles.clear()
    
    for s in stars:
        destroy(s)
    stars.clear()
    
    start_menu.enabled = False
    pause_menu.enabled = False
    game_over_menu.enabled = False
    timer_text.enabled = True
    level_text.enabled = True
    invincible_text.enabled = False
    
    game_active = True
    spawn_obstacle()

def resume_game():
    global game_active
    pause_menu.enabled = False
    timer_text.enabled = True
    level_text.enabled = True
    
    if is_invincible:
        invincible_text.enabled = True
        
    game_active = True
    invoke(spawn_obstacle, delay=0.5)

# --- 1. START MENU ---
Text(text="THE TIMING GAME", parent=start_menu, y=0.35, scale=3, origin=(0,0), color=color.azure)
Button(text='New Game', parent=start_menu, y=0.15, scale=(0.4, 0.1), color=color.azure, on_click=start_new_game)
Button(text='Shop (Coming Soon)', parent=start_menu, y=0.0, scale=(0.4, 0.1), color=color.dark_gray)
Button(text='Settings (Coming Soon)', parent=start_menu, y=-0.15, scale=(0.4, 0.1), color=color.dark_gray)
Button(text='Exit', parent=start_menu, y=-0.30, scale=(0.4, 0.1), color=color.red, on_click=application.quit)

# --- 2. PAUSE MENU ---
Text(text="PAUSED", parent=pause_menu, y=0.35, scale=3, origin=(0,0), color=color.orange)
Button(text='Resume', parent=pause_menu, y=0.15, scale=(0.4, 0.1), color=color.green, on_click=resume_game)
Button(text='Restart', parent=pause_menu, y=0.0, scale=(0.4, 0.1), color=color.orange, on_click=start_new_game)
Button(text='Main Menu', parent=pause_menu, y=-0.15, scale=(0.4, 0.1), color=color.azure, on_click=go_to_main_menu)
Button(text='Quit', parent=pause_menu, y=-0.30, scale=(0.4, 0.1), color=color.red, on_click=application.quit)

# --- 3. GAME OVER MENU ---
Text(text="GAME OVER!", parent=game_over_menu, y=0.35, scale=3, origin=(0,0), color=color.red)
Button(text='Restart', parent=game_over_menu, y=0.15, scale=(0.4, 0.1), color=color.orange, on_click=start_new_game)
Button(text='Main Menu', parent=game_over_menu, y=0.0, scale=(0.4, 0.1), color=color.azure, on_click=go_to_main_menu)
Button(text='Quit', parent=game_over_menu, y=-0.15, scale=(0.4, 0.1), color=color.red, on_click=application.quit)

# ==========================================

def spawn_obstacle():
    global last_spawned_lane, consecutive_spawns
    
    if not game_active:
        return
        
    available_lanes = lanes.copy()
    if consecutive_spawns >= 2 and last_spawned_lane in available_lanes:
        available_lanes.remove(last_spawned_lane)
        
    lane_x = random.choice(available_lanes)
    
    if lane_x == last_spawned_lane:
        consecutive_spawns += 1
    else:
        last_spawned_lane = lane_x
        consecutive_spawns = 1
        
    spawn_distance = 60 + (current_speed * 2)
    
    # 10% chance to spawn an Invincibility Star
    if random.random() < 0.10:
        star = Entity(model='sphere', color=color.yellow, scale=(1.2, 1.2, 1.2), position=(lane_x, 1, player.z + spawn_distance), collider='box')
        star.is_star = True
        stars.append(star)
    else:
        obs = Entity(model='cube', color=color.red, scale=(1.5, 2, 1.5), position=(lane_x, 0, player.z + spawn_distance), collider='box')
        obs.is_obstacle = True
        obstacles.append(obs)
    
    spawn_delay = 15.0 / current_speed
    invoke(spawn_obstacle, delay=spawn_delay)


def update():
    global play_time, current_level, current_speed, game_active, has_crashed
    global is_invincible, invincibility_timer
    
    if not game_active:
        camera.z = player.z - 22
        camera.y = 8
        camera.x = 0
        camera.rotation_x = 18
        return
        
    # 1. UPDATE TIME & PROGRESSION
    play_time += time.dt
    timer_text.text = f'Time: {round(play_time, 1)}'
    
    new_level = int(play_time / 10) + 1
    if new_level > current_level:
        current_level = new_level
        current_speed += 2.0 
        level_text.text = f'Level: {current_level}'
        
    # 2. INVINCIBILITY LOGIC
    if is_invincible:
        invincibility_timer -= time.dt
        
        # Dynamic countdown update (ensures it doesn't drop below 0.0 visually)
        display_time = max(0.0, round(invincibility_timer, 1))
        invincible_text.text = f'INVINCIBLE! {display_time}s'
        
        player.color = color.gold if int(play_time * 10) % 2 == 0 else color.white
        
        if invincibility_timer <= 0:
            is_invincible = False
            player.color = color.orange
            invincible_text.enabled = False
    
    # 3. RUNNING & LANE CHANGING
    player.z += current_speed * time.dt
    player.x = lerp(player.x, lanes[current_lane], time.dt * 10)
    
    # 4. COLLISION DETECTION
    hit_info = player.intersects()
    if hit_info.hit:
        entity = hit_info.entity
        
        if getattr(entity, 'is_star', False):
            is_invincible = True
            invincibility_timer = 5.0
            invincible_text.text = 'INVINCIBLE! 5.0s'
            invincible_text.enabled = True
            destroy(entity)
            if entity in stars:
                stars.remove(entity)
                
        elif getattr(entity, 'is_obstacle', False):
            if not is_invincible:
                has_crashed = True
                game_active = False
                game_over_menu.enabled = True
                timer_text.enabled = False
                level_text.enabled = False
                invincible_text.enabled = False
            else:
                destroy(entity)
                if entity in obstacles:
                    obstacles.remove(entity)
        
    # 5. CLEANUP
    for obs in obstacles:
        if obs.z < player.z - 5:
            destroy(obs)
            obstacles.remove(obs)
            
    for s in stars:
        if s.z < player.z - 5:
            destroy(s)
            stars.remove(s)
    
    # 6. CAMERA SETUP 
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
    global current_lane, is_jumping, is_crouching, game_active
    
    # --- PAUSE MENU (ESC) ---
    if key == 'escape':
        if game_active and not has_crashed:
            game_active = False
            pause_menu.enabled = True
            timer_text.enabled = False
            level_text.enabled = False
            invincible_text.enabled = False
        elif pause_menu.enabled:
            resume_game()
            
    if not game_active:
        return
        
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
            player.animate_y(2, duration=0.3, curve=curve.out_sine)
            def jump_down():
                player.animate_y(0, duration=0.3, curve=curve.in_sine)
            invoke(jump_down, delay=0.3)
            invoke(reset_jump, delay=0.65)
            
    # --- CROUCHING ---
    if key == 'down arrow':
        if not is_crouching and not is_jumping:
            is_crouching = True
            player.animate_scale((1, 1, 1), duration=0.1)
            player.animate_y(-0.5, duration=0.1)
            def stand_up():
                player.animate_scale((1, 2, 1), duration=0.1)
                player.animate_y(0, duration=0.1)
            invoke(stand_up, delay=1.0)
            invoke(reset_crouch, delay=1.15)

app.run()