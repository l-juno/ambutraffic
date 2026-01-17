import pygame


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

ROWS = 6
COLS = 8

TOP_MARGIN = 10
BOTTOM_MARGIN = 10
LEFT_MARGIN = 10
RIGHT_MARGIN = 10

ROAD_COLOR = (50, 50, 50)
BG_COLOR = (30, 30, 30)




def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
