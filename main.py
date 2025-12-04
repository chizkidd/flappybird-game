import pygame
import random
import asyncio # <--- ADDED: Import asyncio for asynchronous web execution

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 400
HEIGHT = 600
# The window creation line remains the same for Pygame-CE in PyScript
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
# BLACK = (0, 0, 0) # Not used after background image was loaded
# GREEN = (0, 255, 0) # Not used after pipe image was loaded

# Game variables
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
high_score = 0

# Game Assets (Ensure these files are in the 'assets' folder in your repo!)
# NOTE: PyScript is case-sensitive and path-sensitive. Use forward slashes!
try:
    bg_img = pygame.image.load('assets/background-day.png').convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    
    bird_img = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
    pipe_img = pygame.image.load('assets/pipe-green.png').convert()
except pygame.error as e:
    # A simple fallback/error message if assets don't load in the browser
    print(f"Error loading assets: {e}. Check asset paths and filenames.")
    bg_img = pygame.Surface((WIDTH, HEIGHT)); bg_img.fill((135, 206, 235)) # Sky Blue Fallback
    bird_img = pygame.Surface((40, 30)); bird_img.fill((255, 255, 0))
    pipe_img = pygame.Surface((70, 400)); pipe_img.fill((0, 128, 0))


bird_rect = bird_img.get_rect(center=(100, HEIGHT // 2))

# Pipes
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
# NOTE: PyScript may have difficulty with pygame.time.set_timer. 
# It's better to manage time-based events manually in the async loop if issues arise.
pygame.time.set_timer(SPAWNPIPE, 1200)

# Font
# Using None defaults to a system font, which should work in PyScript.
game_font = pygame.font.Font(None, 40) 

# --- [Your other functions remain unchanged] ---
def create_pipe():
    # ... (function body unchanged) ...
    random_pipe_pos = random.choice([300, 350, 400])
    bottom_pipe = pipe_img.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_img.get_rect(midbottom=(500, random_pipe_pos - 200))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    # ... (function body unchanged) ...
    for pipe in pipes:
        pipe.centerx -= 5
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(pipes):
    # ... (function body unchanged) ...
    for pipe in pipes:
        if pipe.bottom >= 600:
            window.blit(pipe_img, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_img, False, True)
            window.blit(flip_pipe, pipe)

def check_collision(pipes):
    # ... (function body unchanged) ...
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 600:
        return False
    return True

def rotate_bird(bird):
    # ... (function body unchanged) ...
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird

def score_display(game_state):
    # ... (function body unchanged) ...
    global high_score, score
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, WHITE)
        score_rect = score_surface.get_rect(center=(200, 100))
        window.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(200, 100))
        window.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(200, 500))
        window.blit(high_score_surface, high_score_rect)

def update_score(score, high_score):
    # ... (function body unchanged) ...
    if score > high_score:
        high_score = score
    return high_score

# Game loop
clock = pygame.time.Clock()
# NOTE: Removed 'running = True' as the async function will handle the loop

# <--- MODIFIED: Define the main game loop as an asynchronous function --->
async def main():
    global bird_movement, game_active, score, high_score, pipe_list, bird_rect
    
    # Use global running variable inside the loop instead of a while loop
    running = True 

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Event handling remains the same
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird_movement = 0
                    bird_movement -= 8
                if event.key == pygame.K_SPACE and game_active == False:
                    game_active = True
                    pipe_list.clear()
                    bird_rect.center = (100, 300)
                    bird_movement = 0
                    score = 0

            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipe())

        # window.fill(BLACK)
        window.blit(bg_img, (0, 0))

        if game_active:
            # Bird movement and collision check
            bird_movement += gravity
            rotated_bird = rotate_bird(bird_img)
            bird_rect.centery += bird_movement
            window.blit(rotated_bird, bird_rect)
            game_active = check_collision(pipe_list)

            # Pipes and scoring
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)
            score += 0.01
            score_display('main_game')
        else:
            high_score = update_score(score, high_score)
            score_display('game_over')

        # Update the display
        pygame.display.update()
        
        # Limit frame rate
        clock.tick(60)
        
        # <--- ADDED: Yield control back to the browser's event loop --->
        await asyncio.sleep(0) 

    pygame.quit()

# <--- MODIFIED: Start the asynchronous loop --->
if __name__ == '__main__':
    # This check is good practice, but for PyScript, the following line is key.
    asyncio.run(main())
