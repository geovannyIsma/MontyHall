import pygame
from utils import reset_game

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monty Hall Game")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Cargar imágenes
background_image = pygame.image.load("Assets/escenario1.jpg")
door_sprites = [pygame.image.load(f"Assets/puerta{i}.png") for i in range(1, 6)]
car_image = pygame.image.load("Assets/vehiculo.png")
goat_image = pygame.image.load("Assets/cabra.png")

# Escalado de imágenes
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
door_sprites = [pygame.transform.scale(img, (250, 375)) for img in door_sprites]
car_image = pygame.transform.scale(car_image, (150, 150))
goat_image = pygame.transform.scale(goat_image, (150, 150))

# Cargar sonidos
click_sound = pygame.mixer.Sound("Assets/mixkit-creaky-door-open-195.wav")
win_sound = pygame.mixer.Sound("Assets/sfx-victory1.mp3")
lose_sound = pygame.mixer.Sound("Assets/mixkit-goat-single-baa-1760.wav")

# Fuente para texto
font = pygame.font.SysFont("Arial", 24)
stats_font = pygame.font.SysFont("Arial", 20, bold=True)

PRIZE_SOUND = pygame.USEREVENT + 1

# Variables del juego
doors = [0, 1, 2]
door_positions = [(100, 170), (415, 170), (730, 170)]
door_objects, prizes = reset_game(door_positions, door_sprites, car_image, goat_image)

INDICATOR_COLOR = (0,0, 255)
INDICATOR_WIDTH = 3


selected_door = None
revealed_door = None
final_choice = None
game_state = "select"

# Variables de estadísticas
wins = 0
losses = 0

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            click_sound.play()
            if game_state == "select":
                for door in door_objects:
                    if door.x < event.pos[0] < door.x + 250 and door.y < event.pos[1] < door.y + 375:
                        selected_door = door.door_index
                        game_state = "reveal"
                        break

            elif game_state == "decision":
                if keep_button_x < event.pos[0] < keep_button_x + button_width and button_y < event.pos[1] < button_y + button_height:
                    final_choice = selected_door
                    door_objects[final_choice].open()
                    game_state = "waiting"

                if change_button_x < event.pos[0] < change_button_x + button_width and button_y < event.pos[1] < button_y + button_height:
                    final_choice = [door for door in doors if door != selected_door and door != revealed_door][0]
                    door_objects[final_choice].open()
                    game_state = "waiting"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_state == "end":
                door_objects, prizes = reset_game(door_positions, door_sprites, car_image, goat_image)
                selected_door = None
                revealed_door = None
                final_choice = None
                game_state = "select"

        if event.type == PRIZE_SOUND:
            if prizes[revealed_door] == "car":
                win_sound.play()
            else:
                lose_sound.play()
            pygame.time.set_timer(PRIZE_SOUND, 0)

    if game_state == "reveal" and revealed_door is None:
        for i, prize in enumerate(prizes):
            if i != selected_door and prize == "goat":
                revealed_door = i
                door_objects[i].open()
                break
        pygame.time.set_timer(PRIZE_SOUND, 2500)
        game_state = "decision"

    if game_state == "waiting":
        if door_objects[final_choice].has_faded:
            game_state = "end"
            if prizes[final_choice] == "car":
                wins += 1
                win_sound.play()
            else:
                losses += 1
                lose_sound.play()

    for door in door_objects:
        door.draw(screen)

    if selected_door is not None:
        selected_door_obj = door_objects[selected_door]
        pygame.draw.rect(screen, INDICATOR_COLOR, (selected_door_obj.x - INDICATOR_WIDTH, selected_door_obj.y - INDICATOR_WIDTH, 250 + 2 * INDICATOR_WIDTH, 375 + 2 * INDICATOR_WIDTH), INDICATOR_WIDTH)

    if game_state == "select":
        message = "Selecciona una puerta haciendo clic en ella."
    elif game_state == "reveal":
        message = f"El anfitrión revela una cabra detrás de la puerta {revealed_door + 1}."
    elif game_state == "decision":
        message = "¿Quieres mantener tu elección o cambiar de puerta?"
        button_y = 570
        button_width = 120
        button_height = 40
        button_spacing = 50
        screen_center_x = WIDTH // 2

        keep_button_x = screen_center_x - button_width - button_spacing // 2
        pygame.draw.rect(screen, BLUE, (keep_button_x, button_y, button_width, button_height))
        screen.blit(font.render("Mantener", True, WHITE), (keep_button_x + 20, button_y + 10))

        change_button_x = screen_center_x + button_spacing // 2
        pygame.draw.rect(screen, GREEN, (change_button_x, button_y, button_width, button_height))
        screen.blit(font.render("Cambiar", True, WHITE), (change_button_x + 20, button_y + 10))
    elif game_state == "end":
        if prizes[final_choice] == "car":
            message = "¡Felicidades! Ganaste el coche."
        else:
            message = "Lo siento, obtuviste una cabra."
        door_objects[final_choice].open()
        message += " Presiona 'r' para jugar de nuevo."

    text = font.render(message, True, WHITE)
    screen.blit(text, (50, 50))

    total_games = wins + losses
    win_percentage = (wins / total_games * 100) if total_games > 0 else 0
    stats_text = f"Victorias: {wins}  Pérdidas: {losses}  Porcentaje de victorias: {win_percentage:.2f}%"
    stats_surface = stats_font.render(stats_text, True, WHITE)
    screen.blit(stats_surface, (50, 650))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
