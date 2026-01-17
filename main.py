import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

ROWS = 1
COLS = 1


USABLE_WIDTH = SCREEN_WIDTH
USABLE_HEIGHT = SCREEN_HEIGHT


ROAD_COLOR = (50, 50, 50)
BG_COLOR = (30, 30, 30)

ROAD_THICKNESS = SCREEN_WIDTH // 4

def draw_roads(screen):

    road_rect = pygame.Rect(
        (SCREEN_WIDTH - ROAD_THICKNESS) // 2,
        0,
        ROAD_THICKNESS,
        SCREEN_HEIGHT
    )
    pygame.draw.rect(screen, ROAD_COLOR, road_rect)

    road_rect = pygame.Rect(
        0,
        (SCREEN_HEIGHT - ROAD_THICKNESS) // 2,
        SCREEN_WIDTH,
        ROAD_THICKNESS
    )
    pygame.draw.rect(screen, ROAD_COLOR, road_rect)

    





def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- draw ---
        screen.fill(BG_COLOR)
        draw_roads(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
