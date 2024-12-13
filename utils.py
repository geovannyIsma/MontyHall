import random
from door import Door

def reset_game(door_positions, door_sprites, car_image, goat_image):
    prizes = ["goat"] * (len(door_positions) - 1) + ["car"]
    random.shuffle(prizes)
    door_objects = [Door(x, y, i, door_sprites, car_image, goat_image, prizes) for i, (x, y) in enumerate(door_positions)]
    return door_objects, prizes