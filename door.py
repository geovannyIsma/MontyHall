
class Door:
    def __init__(self, x, y, door_index, door_sprites, car_image, goat_image, prizes):
        self.x = x
        self.y = y
        self.door_index = door_index
        self.door_sprites = door_sprites
        self.car_image = car_image
        self.goat_image = goat_image
        self.prizes = prizes
        self.animation_index = 0
        self.is_opening = False
        self.is_open = False
        self.is_fading = False
        self.has_faded = False
        self.opacity = 255
        self.animation_timer = 0

    def draw(self, surface):
        if self.is_opening and not self.is_open:
            self.animation_timer += 1
            if self.animation_timer >= 5:
                self.animation_timer = 0
                self.animation_index += 1
                if self.animation_index >= len(self.door_sprites):
                    self.is_open = True
                    self.is_fading = True
                    self.animation_index = len(self.door_sprites) - 1

        if self.is_fading:
            self.opacity -= 5
            if self.opacity <= 0:
                self.opacity = 0
                self.is_fading = False
                self.has_faded = True

        if not self.has_faded:
            door_with_opacity = self.set_opacity(self.door_sprites[self.animation_index])
            surface.blit(door_with_opacity, (self.x, self.y))
        else:
            prize_image = self.car_image if self.prizes[self.door_index] == "car" else self.goat_image
            surface.blit(prize_image, (self.x + 75, self.y + 200))

    def open(self):
        if not self.is_open:
            self.is_opening = True

    def set_opacity(self, image):
        image_with_alpha = image.copy()
        image_with_alpha.set_alpha(self.opacity)
        return image_with_alpha