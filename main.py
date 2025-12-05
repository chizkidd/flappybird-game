import pygame
import random
import asyncio 

# Set up the game window variables globally
WIDTH = 400
HEIGHT = 600

# Colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0) # Not used after background image was loaded
# GREEN = (0, 255, 0) # Not used after pipe image was loaded

# Game variables
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
high_score = 0
pipe_list = []

# Game loop variables (initialized in main())
window = None
bg_img = None
bird_img = None
pipe_img = None
bird_rect = None
game_font = None

# --- Helper Functions (Body of the Game Logic) ---

def create_pipe():
    """Creates a new bottom and flipped top pipe pair."""
    random_pipe_pos = random.choice([300, 350, 400])
    # Use global pipe_img variable
    bottom_pipe = pipe_img.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_img.get_rect(midbottom=(500, random_pipe_pos - 200))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    """Moves pipes left and removes off-screen pipes."""
    for pipe in pipes:
        pipe.centerx -= 5
    # Filter out pipes that have moved far left of the screen
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(pipes):
    """Draws the pipes, flipping the top pipe image."""
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            window.blit(pipe_img, pipe)
        else:
            # Flips the pipe image vertically for the top pipe
            flip_pipe = pygame.transform.flip(pipe_img, False, True)
            window.blit(flip_pipe, pipe)

def check_collision(pipes):
    """Checks for collision between the bird and pipes or screen boundaries."""
    # Use global bird_rect variable
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    # Check screen boundaries
    if bird_rect.top <= -100 or bird_rect.bottom >= HEIGHT:
        return False
    return True

def rotate_bird(bird):
    """Rotates the bird image based on its vertical movement."""
    # Use global bird_movement variable
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird

def score_display(game_state):
    """Renders the score and high score display."""
    global high_score, score, window, game_font
    
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
        window.blit(score_surface, score_rect)
        
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
        window.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        window.blit(high_score_surface, high_score_rect)

def update_score(current_score, high_score_val):
    """Updates the high score."""
    if current_score > high_score_val:
        high_score_val = current_score
    return high_score_val

# --- Main Asynchronous Game Loop ---

async def main():
    # Use global variables that will be initialized within this function
    global bird_movement, game_active, score, high_score, pipe_list, bird_rect, window, bg_img, bird_img, pipe_img, game_font
    
    # 1. Initialization (Must be inside the async function for PyScript)
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    
    # Asset Loading
    try:
        # NOTE: Ensure 'assets' folder and files are pushed to GitHub
        bg_img = pygame.image.load('assets/background-day.png').convert()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        bird_img = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
        pipe_img = pygame.image.load('assets/pipe-green.png').convert()
    except pygame.error as e:
        print(f"Error loading assets: {e}. Falling back to basic surfaces.")
        bg_img = pygame.Surface((WIDTH, HEIGHT)); bg_img.fill((135, 206, 235)) 
        bird_img = pygame.Surface((40, 30)); bird_img.fill((255, 255, 0))
        pipe_img = pygame.Surface((70, 400)); pipe_img.fill((0, 128, 0))
        
    bird_rect = bird_img.get_rect(center=(100, HEIGHT // 2))

    # Event Setup
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200)
    game_font = pygame.font.Font(None, 40)
    
    running = True 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird_movement = -8 # Flap strength
                    else: # Restart logic
                        game_active = True
                        pipe_list.clear()
                        bird_rect.center = (100, HEIGHT // 2)
                        bird_movement = 0
                        score = 0

            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipe())

        # 2. Drawing and Logic
        window.blit(bg_img, (0, 0))

        if game_active:
            # Bird Logic
            bird_movement += gravity
            rotated_bird = rotate_bird(bird_img)
            bird_rect.centery += bird_movement
            window.blit(rotated_bird, bird_rect)
            game_active = check_collision(pipe_list)

            # Pipe Logic
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)
            
            # Scoring
            score += 0.01
            score_display('main_game')
        else:
            high_score = update_score(score, high_score)
            score_display('game_over')

        # 3. Update Screen and Yield Control
        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0) # Yield control to the browser loop 

    pygame.quit()

# --- Entry Point ---
if __name__ == '__main__':
    # Start the asynchronous game loop
    asyncio.run(main())
