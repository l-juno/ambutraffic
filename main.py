import pygame
import json
import argparse

from classes.vehicle import Vehicle

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

def load_from_json(path):
    with open(path, "r") as f:
        data = json.load(f)

    vehicles = []
    for v in data["vehicles"]:
        position = pygame.Vector2(v["position"][0], v["position"][1])
        speed = v["speed"]
        vehicle_type = v.get("type")

        vehicles.append(Vehicle(position, speed, vehicle_type))

    return vehicles

def parse_args():
    parser = argparse.ArgumentParser(description="Ambulance Traffic Simulator")
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Path to scenario JSON file"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    vehicles = load_from_json(args.scenario)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        
        for vehicle in vehicles:
            screen.blit(vehicle.image, vehicle.rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
