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
door_sprites = [pygame.image.load(f"Assets/puerta{i}.png") for i in range(1, 6)]
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
game_state = "select"  # "select", "reveal", "decision", "waiting", "end"


# Clase para la animación de la puerta
class Door:
    def __init__(self, x, y, door_index):
        self.x = x
        self.y = y
        self.door_index = door_index
        self.animation_index = 0
        self.is_opening = False
        self.is_open = False
        self.is_fading = False
        self.has_faded = False  # Nuevo estado para controlar el final del desvanecimiento
        self.opacity = 255  # Inicialmente la puerta está completamente visible
        self.animation_timer = 0  # Controlar el tiempo entre cuadros

    def draw(self, surface):
        # Animación de apertura
        if self.is_opening and not self.is_open:
            self.animation_timer += 1
            if self.animation_timer >= 5:  # Cambiar de cuadro cada 5 ticks
                self.animation_timer = 0
                self.animation_index += 1
                if self.animation_index >= len(door_sprites):  # Animación completa
                    self.is_open = True
                    self.is_fading = True
                    self.animation_index = len(door_sprites) - 1  # Fijar en el último cuadro

        # Efecto de desvanecimiento
        if self.is_fading:
            self.opacity -= 5  # Reducir opacidad gradualmente
            if self.opacity <= 0:
                self.opacity = 0
                self.is_fading = False
                self.has_faded = True  # Marcar que el desvanecimiento ha terminado

        # Dibujar la puerta o el premio
        if not self.has_faded:  # Mientras no haya terminado el desvanecimiento
            door_with_opacity = self.set_opacity(door_sprites[self.animation_index])
            surface.blit(door_with_opacity, (self.x, self.y))
        else:
            # Dibujar el premio cuando el desvanecimiento ha terminado
            prize_image = car_image if prizes[self.door_index] == "car" else goat_image
            surface.blit(prize_image, (self.x + 50, self.y + 200))

    def open(self):
        # Comenzar la animación solo si la puerta no está completamente abierta
        if not self.is_open:
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
                    door_objects[final_choice].open()
                    game_state = "waiting"  # Nuevo estado para esperar la animación

                # Botón "Cambiar"
                if 450 < event.pos[0] < 600 and 500 < event.pos[1] < 550:
                    final_choice = [door for door in doors if door != selected_door and door != revealed_door][0]
                    door_objects[final_choice].open()
                    game_state = "waiting"  # Nuevo estado para esperar la animación

    # Lógica del juego
    if game_state == "reveal" and revealed_door is None:
        # Revelar una puerta que no sea la seleccionada ni tenga el coche
        for i, prize in enumerate(prizes):
            if i != selected_door and prize == "goat":
                revealed_door = i
                door_objects[i].open()
                break
        game_state = "decision"

    if game_state == "waiting":
        # Verifica si la puerta seleccionada terminó de abrirse
        if door_objects[final_choice].has_faded:
            game_state = "end"

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

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
