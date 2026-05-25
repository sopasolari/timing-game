from ursina import *

# Initialize the Ursina engine (creates the 3D window)
app = Ursina()

# Create the ground (The running track)
ground = Entity(
    model='plane', 
    color=color.dark_gray, 
    scale=(10, 1, 1000), # X: width, Y: height, Z: length (infinite track)
    position=(0, -1, 0)
)

# Create the player (A simple orange cube for now)
player = Entity(
    model='cube', 
    color=color.orange, 
    scale=(1, 2, 1), # Made taller (Y=2) to resemble a human shape
    position=(0, 0, 0)
)

# The update function runs automatically every frame (Game Loop)
def update():
   # 1. Move the player forward continuously along the Z-axis
    player.z += 10 * time.dt
    
    # 2. Player Input for Left/Right movement (X-axis)
    # Using 'd' / 'right arrow' for right, 'a' / 'left arrow' for left
    if held_keys['d'] or held_keys['right arrow']:
        player.x += 7 * time.dt
    
    if held_keys['a'] or held_keys['left arrow']:
        player.x -= 7 * time.dt
        
    # 3. Boundaries (Keep player from falling off the track)
    # The track is 10 units wide (from -5 to 5)
    if player.x > 4.5:
        player.x = 4.5
    if player.x < -4.5:
        player.x = -4.5
    
    # 4. Camera setup: Follow the player
    camera.z = player.z - 15
    camera.y = 5
    camera.look_at(player)

# Start the game loop
app.run()