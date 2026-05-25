from ursina import *
import random
import json
import os

app = Ursina()

# ==========================================
# --- SAVE / LOAD SYSTEM ---
# ==========================================
SAVE_FILE = 'save_data.json'

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return {'coins': 0, 'emp': 0, 'wings': 0, 'freeze': 0}

def save_data():
    with open(SAVE_FILE, 'w') as f:
        json.dump({'coins': coins, 'emp': inventory['emp'], 'wings': inventory['wings'], 'freeze': inventory['freeze']}, f)

player_data = load_data()
coins = player_data['coins']
inventory = {
    'emp': player_data['emp'],
    'wings': player_data['wings'],
    'freeze': player_data['freeze']
}

# --- GAME STATE ---
game_active = False 
has_crashed = False  
lanes = [-6, -3, 0, 3, 6]
current_lane = 2

# --- TIMING & ECONOMY ---
time_left = 30.0              
total_time_survived = 0.0     
coins_earned_this_run = 0

current_level = 1
current_speed = 15.0  # Αυξημένη αρχική ταχύτητα για περισσότερη δράση!
is_jumping = False
is_crouching = False

# --- POWER-UPS STATE ---
is_invincible = False
invincibility_timer = 0.0

is_flying = False
flying_timer = 0.0

is_frozen = False
freeze_timer = 0.0

last_spawned_lane = None
consecutive_spawns = 0

# --- ENVIRONMENT ---
track = Entity() 

ground = Entity(parent=track, model='plane', color=color.dark_gray, scale=(15, 1, 2000), position=(0, -1, 0))

for line_x in [-4.5, -1.5, 1.5, 4.5]:
    Entity(parent=track, model='cube', color=color.white, scale=(0.1, 0.1, 2000), position=(line_x, -0.95, 0))

for border_x in [-7.5, 7.5]:
    Entity(parent=track, model='cube', color=color.cyan, scale=(0.2, 0.2, 2000), position=(border_x, -0.95, 0))

player = Entity(model='cube', color=color.orange, scale=(1, 2, 1), position=(0, 0, 0), collider='box')

obstacles = []
stars = [] 
clocks = [] 

# ==========================================
# --- UI ELEMENTS ---
# ==========================================
timer_text = Text(text='Time Left: 30.0s', position=(0, 0.45), origin=(0,0), scale=2, color=color.green, enabled=False)
level_text = Text(text='Level: 1', position=(-0.70, 0.45), origin=(-0.5,0), scale=2, color=color.cyan, enabled=False)

hud_coins = Text(text=f'Coins: {coins}', position=(0.85, 0.45), origin=(0.5,0), scale=2, color=color.yellow, enabled=False)
hud_inventory = Text(text='', position=(0, -0.40), origin=(0,0), scale=1.5, color=color.white, enabled=False)

invincible_text = Text(text='INVINCIBLE!', position=(0, 0.35), origin=(0,0), scale=3, color=color.gold, enabled=False)
freeze_text = Text(text='TIME FROZEN!', position=(0, 0.25), origin=(0,0), scale=2, color=color.cyan, enabled=False)

# ==========================================
# --- MENUS SETUP ---
# ==========================================
start_menu = Entity(parent=camera.ui)
shop_menu = Entity(parent=camera.ui, enabled=False)
pause_menu = Entity(parent=camera.ui, enabled=False)
game_over_menu = Entity(parent=camera.ui, enabled=False)

def update_inventory_hud():
    hud_inventory.text = f"[1] EMP Blast: {inventory['emp']} | [2] Wings: {inventory['wings']} | [3] Time Freeze: {inventory['freeze']}"

def open_shop():
    start_menu.enabled = False
    shop_menu.enabled = True
    shop_coins_text.text = f'Your Coins: {coins}'

def close_shop():
    shop_menu.enabled = False
    start_menu.enabled = True
    save_data()

def buy_item(item_id, cost):
    global coins
    if coins >= cost:
        coins -= cost
        inventory[item_id] += 1
        shop_coins_text.text = f'Your Coins: {coins}'
        save_data()
    else:
        shop_coins_text.text = f'Not enough coins! ({coins})'
        shop_coins_text.color = color.red
        invoke(lambda: setattr(shop_coins_text, 'color', color.yellow), delay=0.5)

def go_to_main_menu():
    global game_active, has_crashed, is_invincible, is_flying, is_frozen
    game_active = False
    has_crashed = False
    is_invincible = False
    is_flying = False
    is_frozen = False
    player.color = color.orange
    player.y = 0
    
    start_menu.enabled = True
    pause_menu.enabled = False
    game_over_menu.enabled = False
    timer_text.enabled = False
    level_text.enabled = False
    invincible_text.enabled = False
    freeze_text.enabled = False
    hud_coins.enabled = False
    hud_inventory.enabled = False
    
    save_data()
    
    for obs in obstacles: destroy(obs)
    for s in stars: destroy(s)
    for c in clocks: destroy(c)
    obstacles.clear()
    stars.clear()
    clocks.clear()

def start_new_game():
    global game_active, time_left, total_time_survived, coins_earned_this_run
    global current_level, current_speed, current_lane, has_crashed
    global last_spawned_lane, consecutive_spawns, is_invincible, is_flying, is_frozen
    
    time_left = 30.0
    total_time_survived = 0.0
    coins_earned_this_run = 0
    current_level = 1
    current_speed = 15.0  # Reset speed to new faster baseline
    current_lane = 2
    has_crashed = False
    is_invincible = False
    is_flying = False
    is_frozen = False
    
    player.color = color.orange
    player.position = (0, 0, 0)
    last_spawned_lane = None
    consecutive_spawns = 0
    
    for obs in obstacles: destroy(obs)
    for s in stars: destroy(s)
    for c in clocks: destroy(c)
    obstacles.clear()
    stars.clear()
    clocks.clear()
    
    start_menu.enabled = False
    pause_menu.enabled = False
    game_over_menu.enabled = False
    
    timer_text.enabled = True
    level_text.enabled = True
    hud_coins.enabled = True
    hud_inventory.enabled = True
    hud_coins.text = f'Coins: {coins}'
    update_inventory_hud()
    
    game_active = True
    spawn_obstacle()

def resume_game():
    global game_active
    pause_menu.enabled = False
    timer_text.enabled = True
    level_text.enabled = True
    hud_coins.enabled = True
    hud_inventory.enabled = True
    if is_invincible: invincible_text.enabled = True
    if is_frozen: freeze_text.enabled = True
    game_active = True
    invoke(spawn_obstacle, delay=0.5)

# --- 1. START MENU ---
Text(text="THE TIMING GAME", parent=start_menu, y=0.35, scale=3, origin=(0,0), color=color.azure)
Button(text='New Game', parent=start_menu, y=0.15, scale=(0.4, 0.1), color=color.azure, on_click=start_new_game)
Button(text='Shop & Upgrades', parent=start_menu, y=0.0, scale=(0.4, 0.1), color=color.gold, on_click=open_shop)
Button(text='Exit', parent=start_menu, y=-0.15, scale=(0.4, 0.1), color=color.red, on_click=application.quit)

# --- 2. SHOP MENU ---
Text(text="SHOP", parent=shop_menu, y=0.40, scale=3, origin=(0,0), color=color.gold)
shop_coins_text = Text(text=f'Your Coins: {coins}', parent=shop_menu, y=0.30, scale=2, origin=(0,0), color=color.yellow)

Text(text="[1] EMP Blast: Destroys all obstacles instantly.", parent=shop_menu, y=0.15, origin=(0,0), color=color.white)
Button(text='Buy EMP (Cost: 20)', parent=shop_menu, y=0.08, scale=(0.3, 0.05), color=color.azure, on_click=lambda: buy_item('emp', 20))

Text(text="[2] Wings: Fly above obstacles for 5 seconds.", parent=shop_menu, y=0.0, origin=(0,0), color=color.white)
Button(text='Buy Wings (Cost: 30)', parent=shop_menu, y=-0.07, scale=(0.3, 0.05), color=color.azure, on_click=lambda: buy_item('wings', 30))

Text(text="[3] Time Freeze: Stops countdown for 5 seconds.", parent=shop_menu, y=-0.15, origin=(0,0), color=color.white)
Button(text='Buy Freeze (Cost: 40)', parent=shop_menu, y=-0.22, scale=(0.3, 0.05), color=color.azure, on_click=lambda: buy_item('freeze', 40))

Button(text='Back to Menu', parent=shop_menu, y=-0.35, scale=(0.3, 0.08), color=color.gray, on_click=close_shop)

# --- 3. PAUSE & GAME OVER MENUS ---
Text(text="PAUSED", parent=pause_menu, y=0.35, scale=3, origin=(0,0), color=color.orange)
Button(text='Resume', parent=pause_menu, y=0.15, scale=(0.4, 0.1), color=color.green, on_click=resume_game)
Button(text='Main Menu', parent=pause_menu, y=0.0, scale=(0.4, 0.1), color=color.azure, on_click=go_to_main_menu)

Text(text="GAME OVER!", parent=game_over_menu, y=0.35, scale=3, origin=(0,0), color=color.red)
Button(text='Restart', parent=game_over_menu, y=0.15, scale=(0.4, 0.1), color=color.orange, on_click=start_new_game)
Button(text='Main Menu', parent=game_over_menu, y=0.0, scale=(0.4, 0.1), color=color.azure, on_click=go_to_main_menu)

# ==========================================

def spawn_obstacle():
    global last_spawned_lane, consecutive_spawns, time_left
    if not game_active: return
        
    available_lanes = lanes.copy()
    if consecutive_spawns >= 2 and last_spawned_lane in available_lanes:
        available_lanes.remove(last_spawned_lane)
        
    lane_x = random.choice(available_lanes)
    
    if lane_x == last_spawned_lane: consecutive_spawns += 1
    else: last_spawned_lane = lane_x; consecutive_spawns = 1
        
    spawn_distance = 60 + (current_speed * 2)
    spawn_chance = random.random()
    
    if time_left > 30.0:
        clock_threshold = 0.105 
    elif time_left <= 15.0 and len(clocks) == 0:
        clock_threshold = 0.40
    else:
        clock_threshold = 0.12

    if spawn_chance < 0.10: 
        star = Entity(model='sphere', color=color.yellow, scale=(1.2, 1.2, 1.2), position=(lane_x, 1, player.z + spawn_distance), collider='box')
        star.is_star = True
        stars.append(star)
    elif spawn_chance < clock_threshold: 
        clock = Entity(model='sphere', color=color.cyan, scale=(1.2, 1.2, 1.2), position=(lane_x, 2.5, player.z + spawn_distance), collider='box')
        clock.is_time_bonus = True
        clocks.append(clock)
    else:
        if random.random() < 0.5:
            obs = Entity(model='cube', color=color.red, scale=(1.5, 2, 1.5), position=(lane_x, 0, player.z + spawn_distance), collider='box')
        else:
            obs = Entity(model='cube', color=color.red, scale=(1.5, 1.5, 1.5), position=(lane_x, 1.2, player.z + spawn_distance), collider='box')
            
        obs.is_obstacle = True
        obstacles.append(obs)
    
    spawn_delay = 15.0 / current_speed
    invoke(spawn_obstacle, delay=spawn_delay)


def update():
    global time_left, total_time_survived, coins_earned_this_run, coins
    global current_level, current_speed, game_active, has_crashed
    global is_invincible, invincibility_timer, is_flying, flying_timer, is_frozen, freeze_timer
    
    if not game_active:
        camera.z = player.z - 22; camera.y = 8; camera.x = 0; camera.rotation_x = 18
        return
        
    # 1. UPDATE TIMERS & COINS
    if not is_frozen:
        time_left -= time.dt
    else:
        freeze_timer -= time.dt
        freeze_text.text = f'FROZEN! {round(freeze_timer, 1)}s'
        if freeze_timer <= 0:
            is_frozen = False
            freeze_text.enabled = False
            
    total_time_survived += time.dt
    
    if int(total_time_survived) > coins_earned_this_run:
        coins += 1
        coins_earned_this_run += 1
        hud_coins.text = f'Coins: {coins}'
    
    if time_left <= 0.0:
        time_left = 0.0
        has_crashed = True
        game_active = False
        game_over_menu.enabled = True
        timer_text.enabled = False
        level_text.enabled = False
        hud_coins.enabled = False
        hud_inventory.enabled = False
        save_data()
        
    timer_text.text = f'Time Left: {round(time_left, 1)}s'
    timer_text.color = color.red if time_left <= 15.0 else color.green
    
    new_level = int(total_time_survived / 10) + 1
    if new_level > current_level:
        current_level = new_level
        current_speed += 2.0 
        level_text.text = f'Level: {current_level}'
        
    # 2. POWER-UP LOGIC
    if is_invincible:
        invincibility_timer -= time.dt
        invincible_text.text = f'INVINCIBLE! {max(0.0, round(invincibility_timer, 1))}s'
        player.color = color.gold if int(total_time_survived * 10) % 2 == 0 else color.white
        if invincibility_timer <= 0:
            is_invincible = False
            player.color = color.orange
            invincible_text.enabled = False

    if is_flying:
        flying_timer -= time.dt
        if flying_timer <= 0:
            is_flying = False
            player.animate_y(0, duration=0.3) 
    
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
            invincible_text.enabled = True
            destroy(entity)
            if entity in stars: stars.remove(entity)
                
        elif getattr(entity, 'is_time_bonus', False):
            time_left += 10.0
            destroy(entity)
            if entity in clocks: clocks.remove(entity)
                
        elif getattr(entity, 'is_obstacle', False):
            if not is_flying:
                if not is_invincible:
                    has_crashed = True
                    game_active = False
                    game_over_menu.enabled = True
                    timer_text.enabled = False
                    level_text.enabled = False
                    hud_coins.enabled = False
                    hud_inventory.enabled = False
                    save_data()
                else:
                    # INVINCIBLE SMASH
                    time_left += 2.0
                    destroy(entity)
                    if entity in obstacles: obstacles.remove(entity)
        
    # 5. CLEANUP & DODGE REWARDS
    for obs in obstacles:
        if obs.z < player.z - 5: 
            if current_level >= 10:
                time_left += 0.1
            elif current_level >= 5:
                time_left += 0.2
            else:
                time_left += 0.5
                
            destroy(obs)
            obstacles.remove(obs)
            
    for s in stars:
        if s.z < player.z - 5: destroy(s); stars.remove(s)
    for c in clocks:
        if c.z < player.z - 5: destroy(c); clocks.remove(c)
    
    # 6. CAMERA SETUP 
    camera.z = player.z - 22
    camera.y = 8
    camera.x = 0
    camera.rotation_x = 18

    # 7. INFINITE TRACK
    track.z = player.z

def reset_jump(): global is_jumping; is_jumping = False
def reset_crouch(): global is_crouching; is_crouching = False

def input(key):
    global current_lane, is_jumping, is_crouching, game_active
    global is_flying, flying_timer, is_frozen, freeze_timer
    
    if key == 'escape':
        if game_active and not has_crashed:
            game_active = False
            pause_menu.enabled = True
            timer_text.enabled = False
            level_text.enabled = False
        elif pause_menu.enabled:
            resume_game()
            
    if not game_active: return
    
    # --- POWER-UP HOTKEYS ---
    if key == '1':
        if inventory['emp'] > 0:
            inventory['emp'] -= 1
            update_inventory_hud()
            for obs in obstacles: destroy(obs)
            obstacles.clear()
            
    if key == '2':
        if inventory['wings'] > 0 and not is_flying:
            inventory['wings'] -= 1
            update_inventory_hud()
            is_flying = True
            flying_timer = 5.0
            player.animate_y(4, duration=0.3) 
            
    if key == '3':
        if inventory['freeze'] > 0 and not is_frozen:
            inventory['freeze'] -= 1
            update_inventory_hud()
            is_frozen = True
            freeze_timer = 5.0
            freeze_text.enabled = True
    
    # --- MOVEMENT ---
    if key == 'd' or key == 'right arrow':
        if current_lane < 4: current_lane += 1
            
    if key == 'a' or key == 'left arrow':
        if current_lane > 0: current_lane -= 1
            
    if is_flying: return
    
    if key == 'space' or key == 'up arrow':
        if not is_jumping and not is_crouching:
            is_jumping = True
            player.animate_y(2, duration=0.3, curve=curve.out_sine)
            def jump_down(): player.animate_y(0, duration=0.3, curve=curve.in_sine)
            invoke(jump_down, delay=0.3)
            invoke(reset_jump, delay=0.65)
            
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