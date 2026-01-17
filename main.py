import pygame


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

ROWS = 1
COLS = 1

ROAD_COLOR = (50, 50, 50)
BG_COLOR = (30, 30, 30)

ROAD_THICKNESS = SCREEN_WIDTH // 5

NODE_RADIUS = 8
NODE_COLOR = (200, 0, 0)
TEXT_COLOR = (255, 255, 255)

def get_nodes():
    halfX = SCREEN_WIDTH // 2
    halfY = SCREEN_HEIGHT // 2
    halfRoad = ROAD_THICKNESS // 2
    offset = ROAD_THICKNESS // 4

    return [
        (0, (halfX - offset, halfY - (halfRoad+offset))),
        (1, (halfX + offset, halfY - (halfRoad+offset))),
        (2, (halfX + (halfRoad+offset), halfY - offset)),
        (3, (halfX + (halfRoad+offset), halfY + offset)),
        (4, (halfX + offset, halfY + (halfRoad+offset))),
        (5, (halfX - offset, halfY + (halfRoad+offset))),
        (6, (halfX - (halfRoad+offset), halfY + offset)),
        (7, (halfX - (halfRoad+offset), halfY - offset)),
    ]


def draw_roads(screen):
    # horizontal road
    road_rect = pygame.Rect((SCREEN_WIDTH - ROAD_THICKNESS) // 2, 0, ROAD_THICKNESS, SCREEN_HEIGHT)
    pygame.draw.rect(screen, ROAD_COLOR, road_rect)
    # vertical road
    road_rect = pygame.Rect(0, (SCREEN_HEIGHT - ROAD_THICKNESS) // 2, SCREEN_WIDTH, ROAD_THICKNESS)
    pygame.draw.rect(screen, ROAD_COLOR, road_rect)

    
def draw_nodes(screen, font):
    for node_id, (x, y) in get_nodes():
        pygame.draw.circle(screen, NODE_COLOR, (x, y), NODE_RADIUS)

        label = font.render(str(node_id), True, TEXT_COLOR)
        screen.blit(label, (x + 10, y - 10))




def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        draw_roads(screen)
        draw_nodes(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



if __name__ == "__main__":
    main()
