import pygame
import random
import asyncio
import sys

# Constants
WIDTH = 400
HEIGHT = 600
GRAVITY = 0.25

# Helper Functions
def create_pipe(pipe_img):
    random_pipe_pos = random.choice([300, 350, 400])
    bottom_pipe = pipe_img.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_img.get_rect(midbottom=(500, random_pipe_pos - 200))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(window, pipes, pipe_img):
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            window.blit(pipe_img, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_img, False, True)
            window.blit(flip_pipe, pipe)

def check_collision(bird_rect, pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= HEIGHT:
        return False
    return True

def rotate_bird(bird_img, bird_movement):
    return pygame.transform.rotozoom(bird_img, -bird_movement * 3, 1)

def score_display(window, game_state, score, high_score, game_font):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
        window.blit(score_surface, score_rect)
    elif game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
        window.blit(score_surface, score_rect)
        high_score_surface = game_font.render(f'High score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        window.blit(high_score_surface, high_score_rect)

def update_score(score, high_score):
    return max(score, high_score)

async def main():
    print("Initializing Flappy Bird...")
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()

    # Load Assets
    try:
        print("Loading assets from ./assets/...")
        bg_img = pygame.image.load('assets/background-day.png').convert()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        bird_img = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
        pipe_img = pygame.image.load('assets/pipe-green.png').convert()
        print("Assets loaded successfully!")
    except Exception as e:
        print(f"Asset error (check paths): {e}. Using fallbacks.")
        bg_img = pygame.Surface((WIDTH, HEIGHT))
        bg_img.fill((135, 206, 235))  # Sky
        bird_img = pygame.Surface((40, 30))
        bird_img.fill((255, 255, 0))  # Yellow bird
        pipe_img = pygame.Surface((70, 400))
        pipe_img.fill((0, 128, 0))  # Green pipe

    bird_rect = bird_img.get_rect(center=(100, HEIGHT // 2))

    # Setup
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200)
    game_font = pygame.font.Font(None, 40)

    # Variables
    bird_movement = 0
    game_active = True
    score = 0
    high_score = 0
    pipe_list = []

    print("Starting game loop...")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird_movement = -8
                    else:
                        game_active = True
                        pipe_list.clear()
                        bird_rect.center = (100, HEIGHT // 2)
                        bird_movement = 0
                        score = 0
            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipe(pipe_img))

        # Render
        window.blit(bg_img, (0, 0))

        if game_active:
            bird_movement += GRAVITY
            rotated_bird = rotate_bird(bird_img, bird_movement)
            bird_rect.centery += bird_movement
            window.blit(rotated_bird, bird_rect)
            game_active = check_collision(bird_rect, pipe_list)

            pipe_list = move_pipes(pipe_list)
            draw_pipes(window, pipe_list, pipe_img)

            score += 0.01
            score_display(window, 'main_game', score, high_score, game_font)
        else:
            high_score = update_score(score, high_score)
            score_display(window, 'game_over', score, high_score, game_font)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1 / 60)  # Yield to browser—CRITICAL for rendering!

    pygame.quit()
    print("Game ended.")

# Run in PyScript
asyncio.run(main())
