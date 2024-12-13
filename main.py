import pygame
from utils import reset_game

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 1500, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monty Hall Game")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (44, 44, 44)
YELLOW = (255, 255, 0)

# Cargar imágenes
background_image = pygame.image.load("Assets/sprites/escenario1.jpg")
door_sprites = [pygame.image.load(f"Assets/sprites/puerta{i}.png") for i in range(1, 6)]
car_image = pygame.image.load("Assets/sprites/vehiculo.png")
goat_image = pygame.image.load("Assets/sprites/cabra.png")

# Escalado de imágenes
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
door_sprites = [pygame.transform.scale(img, (250, 375)) for img in door_sprites]
car_image = pygame.transform.scale(car_image, (150, 150))
goat_image = pygame.transform.scale(goat_image, (150, 150))

# Cargar sonidos
click_sound = pygame.mixer.Sound("Assets/songs/mixkit-creaky-door-open-195.wav")
win_sound = pygame.mixer.Sound("Assets/songs/sfx-victory1.mp3")
lose_sound = pygame.mixer.Sound("Assets/songs/mixkit-goat-single-baa-1760.wav")

click_sound.set_volume(0.3)  # 50% del volumen máximo
win_sound.set_volume(0.3)    # 50% del volumen máximo
lose_sound.set_volume(0.3)   # 50% del volumen máximo

# Fuente para texto
font = pygame.font.SysFont("Arial", 24)
stats_font = pygame.font.SysFont("Arial", 20, bold=True)

PRIZE_SOUND = pygame.USEREVENT + 1

# Niveles de dificultad
difficulty_levels = {
    "easy": {"num_doors": 3, "time_limit": 15},
    "medium": {"num_doors": 4, "time_limit": 10},
    "hard": {"num_doors": 5, "time_limit": 5},
}

# Variables del juego
selected_level = None
game_state = "select_level"
doors = []
door_positions = []
door_objects = []
prizes = []

INDICATOR_COLOR = (0, 0, 255)
INDICATOR_WIDTH = 2

selected_door = None
revealed_door = None
final_choice = None

# Variables de estadísticas
wins = 0
losses = 0

# Variables del temporizador
timer_start = 0
timer_limit = 10  # 10 segundos para tomar una decisión

# Cargar una fuente personalizada
timer_font = pygame.font.Font("Assets/fonts/digital-7 (mono italic).ttf", 30)

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "select_level":
                if easy_button.collidepoint(event.pos):
                    selected_level = "easy"
                elif medium_button.collidepoint(event.pos):
                    selected_level = "medium"
                elif hard_button.collidepoint(event.pos):
                    selected_level = "hard"
                if selected_level:
                    num_doors = difficulty_levels[selected_level]["num_doors"]
                    timer_limit = difficulty_levels[selected_level]["time_limit"]
                    door_positions = [(25 + i * 300, 170) for i in range(num_doors)]
                    door_objects, prizes = reset_game(door_positions, door_sprites, car_image, goat_image)
                    game_state = "select"

            if game_state == "select":
                for door in door_objects:
                    if door.x < event.pos[0] < door.x + 250 and door.y < event.pos[1] < door.y + 375:
                        click_sound.play()
                        selected_door = door.door_index
                        game_state = "reveal"
                        timer_start = pygame.time.get_ticks()  # Iniciar temporizador
                        break

            elif game_state == "decision":
                if keep_button_x < event.pos[0] < keep_button_x + button_width and button_y < event.pos[1] < button_y + button_height:
                    final_choice = selected_door
                    door_objects[final_choice].open()
                    game_state = "waiting"

                if change_button_x < event.pos[0] < change_button_x + button_width and button_y < event.pos[
                    1] < button_y + button_height:
                    game_state = "change"

            elif game_state == "change":
                for door in door_objects:
                    if door.x < event.pos[0] < door.x + 250 and door.y < event.pos[1] < door.y + 375:
                        if door.door_index != selected_door and not door.is_open:
                            click_sound.play()
                            final_choice = door.door_index
                            door_objects[final_choice].open()
                            game_state = "waiting"
                            break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_state == "end":
                door_objects, prizes = reset_game(door_positions, door_sprites, car_image, goat_image)
                selected_door = None
                revealed_door = None
                final_choice = None
                game_state = "select"
            elif event.key == pygame.K_x:
                running = False

        if event.type == PRIZE_SOUND:
            if prizes[revealed_door] == "car":
                win_sound.play()
            else:
                lose_sound.play()
            pygame.time.set_timer(PRIZE_SOUND, 0)

    if game_state == "reveal" and revealed_door is None:
        revealed_doors = []
        for i, prize in enumerate(prizes):
            if i != selected_door and prize == "goat":
                revealed_doors.append(i)
                door_objects[i].open()
                if len(revealed_doors) == len(door_objects) - 2:
                    break
        revealed_door = revealed_doors[0]  # Solo para mantener la lógica existente
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

    if game_state == "decision":
        elapsed_time = (pygame.time.get_ticks() - timer_start) / 1000
        if elapsed_time > timer_limit:
            final_choice = selected_door
            door_objects[final_choice].open()
            game_state = "waiting"
        else:
            remaining_time = timer_limit - elapsed_time
            timer_text = timer_font.render(f"{remaining_time:.1f}s", True, RED)

            # Calcula las dimensiones y la posición del rectángulo
            timer_rect = timer_text.get_rect(topleft=(WIDTH - 100, 50))
            timer_rect.inflate_ip(15, 15)  # Añade un margen alrededor del texto

            pygame.draw.rect(screen, GRAY, timer_rect)

            screen.blit(timer_text, (WIDTH - 100, 50))

    for door in door_objects:
        door.draw(screen)

    if selected_door is not None:
        selected_door_obj = door_objects[selected_door]
        pygame.draw.rect(screen, INDICATOR_COLOR, (selected_door_obj.x - INDICATOR_WIDTH, selected_door_obj.y - INDICATOR_WIDTH, 250 + 2 * INDICATOR_WIDTH, 375 + 2 * INDICATOR_WIDTH), INDICATOR_WIDTH)

    if game_state == "select_level":
        easy_button = pygame.draw.rect(screen, GREEN, (50, 50, 200, 50))
        medium_button = pygame.draw.rect(screen, YELLOW, (300, 50, 200, 50))
        hard_button = pygame.draw.rect(screen, RED, (550, 50, 200, 50))
        screen.blit(font.render("3 Puertas", True, BLACK), (100, 60))
        screen.blit(font.render("4 Puertas", True, BLACK), (350, 60))
        screen.blit(font.render("5 Puertas", True, BLACK), (600, 60))
        message = ""

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
        message += " Presiona 'r' para jugar de nuevo y 'x' para salir."

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