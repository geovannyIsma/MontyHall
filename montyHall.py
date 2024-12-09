import pygame
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monty Hall Game")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Cargar imágenes
door_sprites = [pygame.image.load(f"Assets/puerta{i}.png") for i in range(1,6)]  # Cambia los nombres según tus imágenes
car_image = pygame.image.load("Assets/vehiculo.png")
goat_image = pygame.image.load("Assets/cabra.png")

# Escalado de imágenes
door_sprites = [pygame.transform.scale(img, (200, 400)) for img in door_sprites]
car_image = pygame.transform.scale(car_image, (100, 100))
goat_image = pygame.transform.scale(goat_image, (100, 100))

# Fuente para texto
font = pygame.font.SysFont("Arial", 24)

# Variables del juego
doors = [0, 1, 2]  # Tres puertas
prizes = ["goat", "goat", "car"]
random.shuffle(prizes)

selected_door = None
revealed_door = None
final_choice = None
game_state = "select"  # "select", "reveal", "decision", "end"


# Clase para la animación de la puerta
class Door:
    def __init__(self, x, y, door_index):
        self.x = x
        self.y = y
        self.door_index = door_index
        self.animation_index = 0
        self.is_opening = False
        self.is_open = False
        self.opacity = 255  # Inicialmente la puerta está completamente visible

    def draw(self, surface):
        # Dibujar la puerta con opacidad si está desvaneciéndose
        if self.is_opening:
            if self.opacity > 0:
                self.opacity -= 10  # Reducir la opacidad para crear el efecto de desvanecimiento
            else:
                self.is_open = True
                self.opacity = 255  # Restablecer opacidad para la imagen del premio

        if not self.is_open:
            # Dibuja la puerta con opacidad
            door_with_opacity = self.set_opacity(door_sprites[self.animation_index])
            surface.blit(door_with_opacity, (self.x, self.y))
        else:
            # Si la puerta está abierta, se dibuja el premio
            prize_image = car_image if prizes[self.door_index] == "car" else goat_image
            surface.blit(prize_image, (self.x + 50, self.y + 200))

    def open(self):
        self.is_opening = True

    def set_opacity(self, image):
        # Crear una nueva superficie con la misma imagen pero con transparencia (opacidad)
        image_with_alpha = image.copy()
        image_with_alpha.set_alpha(self.opacity)  # Establecer la opacidad
        return image_with_alpha


# Crear puertas
door_positions = [(100, 100), (300, 100), (500, 100)]
door_objects = [Door(x, y, i) for i, (x, y) in enumerate(door_positions)]

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "select":
                for door in door_objects:
                    if door.x < event.pos[0] < door.x + 200 and door.y < event.pos[1] < door.y + 400:
                        selected_door = door.door_index
                        game_state = "reveal"
                        break

            elif game_state == "decision":
                # Botón "Mantener"
                if 200 < event.pos[0] < 350 and 500 < event.pos[1] < 550:
                    final_choice = selected_door
                    game_state = "end"

                # Botón "Cambiar"
                if 450 < event.pos[0] < 600 and 500 < event.pos[1] < 550:
                    final_choice = [door for door in doors if door != selected_door and door != revealed_door][0]
                    game_state = "end"

    # Lógica del juego
    if game_state == "reveal" and revealed_door is None:
        # Revelar una puerta que no sea la seleccionada ni tenga el coche
        for i, prize in enumerate(prizes):
            if i != selected_door and prize == "goat":
                revealed_door = i
                door_objects[i].open()
                break
        game_state = "decision"

    # Dibujar puertas
    for door in door_objects:
        door.draw(screen)

    # Mostrar mensajes
    if game_state == "select":
        message = "Selecciona una puerta haciendo clic en ella."
    elif game_state == "reveal":
        message = f"El anfitrión revela una cabra detrás de la puerta {revealed_door + 1}."
    elif game_state == "decision":
        message = "¿Quieres mantener tu elección o cambiar de puerta?"
        # Dibujar botones
        pygame.draw.rect(screen, BLUE, (200, 500, 150, 50))
        pygame.draw.rect(screen, GREEN, (450, 500, 150, 50))
        screen.blit(font.render("Mantener", True, WHITE), (220, 515))
        screen.blit(font.render("Cambiar", True, WHITE), (470, 515))
    elif game_state == "end":
        if prizes[final_choice] == "car":
            message = "¡Felicidades! Ganaste el coche."
        else:
            message = "Lo siento, obtuviste una cabra."
        door_objects[final_choice].open()

    # Mostrar texto
    text = font.render(message, True, BLACK)
    screen.blit(text, (50, 50))

    # Mostrar el resultado final
    if game_state == "end":
        for i, door in enumerate(door_objects):
            if door.is_open:
                if prizes[i] == "car":
                    screen.blit(car_image, (door.x + 50, door.y + 200))
                else:
                    screen.blit(goat_image, (door.x + 50, door.y + 200))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
