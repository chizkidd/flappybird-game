# main.py – works with pygame-web in PyScript (Dec 2025)
import pygame
import random
import asyncio

WIDTH, HEIGHT = 400, 600
GRAVITY = 0.25
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load assets (they are in the repo, so this works)
try:
    bg = pygame.image.load("assets/background-day.png").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    bird_img = pygame.image.load("assets/bluebird-midflap.png").convert_alpha()
    pipe_img = pygame.image.load("assets/pipe-green.png").convert()
except Exception as e:
    print("Asset load failed:", e)
    bg = pygame.Surface((WIDTH, HEIGHT)); bg.fill((135, 206, 235))
    bird_img = pygame.Surface((40, 30)); bird_img.fill((255, 255, 0))
    pipe_img = pygame.Surface((70, 400)); pipe_img.fill((0, 128, 0))

# Game objects
bird_rect = bird_img.get_rect(center=(100, HEIGHT//2))
bird_movement = 0
pipes = []
score = 0
high_score = 0
game_active = True
font = pygame.font.Font(None, 50)

SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

def create_pipe():
    y = random.randint(300, 450)
    bottom = pipe_img.get_rect(midtop=(WIDTH + 50, y))
    top    = pipe_img.get_rect(midbottom=(WIDTH + 50, y - 200))
    return bottom, top

async def main():
    global bird_movement, game_active, score, high_score, pipes

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_active:
                    bird_movement = -8
                else:  # restart
                    game_active = True
                    pipes.clear()
                    bird_rect.center = (100, HEIGHT//2)
                    bird_movement = 0
                    score = 0
            if event.type == SPAWNPIPE and game_active:
                pipes.extend(create_pipe())

        screen.blit(bg, (0, 0))

        if game_active:
            # Bird physics
            bird_movement += GRAVITY
            bird_rect.centery += bird_movement
            rotated_bird = pygame.transform.rotozoom(bird_img, -bird_movement * 3, 1)
            screen.blit(rotated_bird, bird_rect)

            # Pipes
            pipes = [p for p in pipes if (p := p.move(-4, 0)).right > -100]
            for pipe in pipes:
                if pipe.bottom >= HEIGHT:
                    screen.blit(pipe_img, pipe)
                else:
                    screen.blit(pygame.transform.flip(pipe_img, False, True), pipe)

            # Collision
            if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT or any(bird_rect.colliderect(p) for p in pipes):
                game_active = False
                high_score = max(high_score, int(score))

            score += 0.02
            score_surf = font.render(str(int(score)), True, "white")
            screen.blit(score_surf, score_surf.get_rect(center=(WIDTH//2, 80)))
        else:
            # Game over screen
            s = font.render(f"Score: {int(score)}", True, "white")
            h = font.render(f"Best: {high_score}", True, "white")
            screen.blit(s, s.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            screen.blit(h, h.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)  # let the browser breathe

asyncio.run(main())
