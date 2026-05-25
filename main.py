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
    # Move the player forward continuously along the Z-axis
    # time.dt ensures smooth movement regardless of the computer's frame rate
    player.z += 10 * time.dt
    
    # Camera setup: Follow the player from behind and slightly above
    camera.z = player.z - 15
    camera.y = 5
    
    # Force the camera to always focus on the player
    camera.look_at(player)

# Start the game loop
app.run()