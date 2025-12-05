import pygame
import random
import asyncio  # Required for browser sync

# Constants
WIDTH, HEIGHT = 400, 600
GRAVITY = 0.5
PIPE_SPEED = 5

# Init (runs once)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)

# Load assets with fallback
try:
    bg = pygame.image.load("assets/background-day.png").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    bird_img = pygame.image.load("assets/bluebird-midflap.png").convert_alpha()
    pipe_img = pygame.image.load("assets/pipe-green.png").convert()
    print("Assets loaded")
except Exception as e:
    print("Assets fallback:", e)
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((135, 206, 250))  # Sky blue
    bird_img = pygame.Surface((34, 24))
    bird_img.fill((255, 255, 0))  # Yellow bird
    pipe_img = pygame.Surface((52, 320))
    pipe_img.fill((0, 200, 0))  # Green pipe

# Game state
bird_rect = bird_img.get_rect(center=(100, HEIGHT//2))
bird_movement = 0
pipes = []
score = 0
game_active = True

def create_pipe():
    y = random.randint(200, 400)
    bottom = pipe_img.get_rect(midtop=(WIDTH + 100, y))
    top = pipe_img.get_rect(midbottom=(WIDTH + 100, y - 180))
    return [bottom, top]

# Async main loop (REQUIRED for pygbag/browser)
async def main():
    global bird_movement, game_active, score, pipes
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_movement = -10
                    if not game_active:
                        # Restart
                        game_active = True
                        pipes = []
                        bird_rect.center = (100, HEIGHT//2)
                        bird_movement = 0
                        score = 0
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:  # Touch support
                bird_movement = -10
                if not game_active:
                    game_active = True
                    pipes = []
                    bird_rect.center = (100, HEIGHT//2)
                    bird_movement = 0
                    score = 0
            if event.type == SPAWNPIPE and game_active:
                pipes.extend(create_pipe())

        # Update
        if game_active:
            bird_movement += GRAVITY
            bird_rect.centery += bird_movement
            
            # Move pipes
            pipes = [p.move(-PIPE_SPEED, 0) for p in pipes if p.right > -50]
            
            # Collision
            if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
                game_active = False
            for pipe in pipes:
                if bird_rect.colliderect(pipe):
                    game_active = False
                    break
            
            score += 0.01

        # Draw
        screen.blit(bg, (0, 0))
        
        if game_active:
            rotated_bird = pygame.transform.rotozoom(bird_img, -bird_movement * 3, 1)
            screen.blit(rotated_bird, bird_rect)
            
            # Draw pipes
            for pipe in pipes:
                if pipe.bottom >= HEIGHT:
                    screen.blit(pipe_img, pipe)
                else:
                    screen.blit(pygame.transform.flip(pipe_img, False, True), pipe)
            
            # Score
            score_text = font.render(str(int(score)), True, (255, 255, 255))
            screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, 80)))
        else:
            # Game Over
            score_text = font.render(f"Score: {int(score)}", True, (255, 255, 255))
            restart_text = pygame.font.Font(None, 36).render("SPACE or TAP to restart", True, (255, 255, 255))
            screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # CRITICAL: Yields to browser for smooth rendering

# Start the game
asyncio.run(main())
