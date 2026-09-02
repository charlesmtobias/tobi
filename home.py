import pygame
import sys
import json
import theme

pygame.init()

# --- Actual display setup ---
# On the Pi, this will be 1024x600 natively (no letterboxing needed).
# On a dev monitor, this is the monitor's real resolution, letterboxed to preview the 7" screen.
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("tobi - Home")

# All drawing happens on this fixed-size surface - never draw to `screen` directly
game_surface = pygame.Surface((theme.GAME_WIDTH, theme.GAME_HEIGHT))

# --- Compute letterbox scale + position once ---
scale = min(SCREEN_WIDTH / theme.GAME_WIDTH, SCREEN_HEIGHT / theme.GAME_HEIGHT)
scaled_width = int(theme.GAME_WIDTH * scale)
scaled_height = int(theme.GAME_HEIGHT * scale)
offset_x = (SCREEN_WIDTH - scaled_width) // 2
offset_y = (SCREEN_HEIGHT - scaled_height) // 2


def screen_to_game_pos(pos):
    """Translate real screen/mouse coordinates into game_surface coordinates."""
    x, y = pos
    game_x = (x - offset_x) / scale
    game_y = (y - offset_y) / scale
    return (game_x, game_y)


font = pygame.font.Font(theme.FONT_PATH, theme.FONT_SIZE_BODY)
title_font = pygame.font.Font(theme.FONT_PATH, theme.FONT_SIZE_TITLE)

# --- Content structure ---
# Subjects and their activities are loaded from content.json rather than
# hardcoded here, so new apps/subjects can be added without editing this file.
with open("content.json", "r") as f:
    subjects = json.load(f)

subject_names = list(subjects.keys())

# --- Grid layout config ---
# NOTE: all layout math uses theme.GAME_WIDTH/HEIGHT (the virtual 1024x600 canvas),
# not SCREEN_WIDTH/SCREEN_HEIGHT (the real monitor) - the scaling step handles the rest.
grid_width = theme.GAME_WIDTH - (2 * theme.MARGIN)
grid_height = theme.GAME_HEIGHT - (2 * theme.MARGIN)

tile_width = (grid_width - (theme.TILE_GAP * (theme.COLS - 1))) // theme.COLS
tile_height = (grid_height - (theme.TILE_GAP * (theme.ROWS - 1))) // theme.ROWS


def get_tile_rect(index, cols=theme.COLS, gap=theme.TILE_GAP, margin=theme.MARGIN,
                   t_width=tile_width, t_height=tile_height):
    col = index % cols
    row = index // cols
    x = margin + col * (t_width + gap)
    y = margin + row * (t_height + gap)
    return pygame.Rect(x, y, t_width, t_height)


# Cartridge slot occupies the first tile position; subjects follow after it.
cartridge_index = 0
cartridge_rect = get_tile_rect(cartridge_index)

home_tiles = []
for i, name in enumerate(subject_names):
    home_tiles.append({"rect": get_tile_rect(i + 1), "label": name})


def cartridge_inserted():
    # Placeholder - real USB detection happens once this runs on the Pi
    return False


# --- App state ---
# current_screen is either "home" or a subject name (e.g. "Science")
current_screen = "home"


def draw_tile(rect, label, color, hovered=False):
    draw_color = theme.TILE_HOVER_COLOR if hovered else color
    pygame.draw.rect(game_surface, draw_color, rect, border_radius=16)
    text_surface = font.render(label, True, theme.TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    game_surface.blit(text_surface, text_rect)


def draw_home_screen(game_mouse_pos):
    game_surface.fill(theme.BG_COLOR)

    for tile in home_tiles:
        hovered = tile["rect"].collidepoint(game_mouse_pos)
        draw_tile(tile["rect"], tile["label"], theme.TILE_COLOR, hovered)

    if cartridge_inserted():
        hovered = cartridge_rect.collidepoint(game_mouse_pos)
        draw_tile(cartridge_rect, "Cartridge", theme.TILE_COLOR, hovered)
    else:
        pygame.draw.rect(game_surface, theme.CARTRIDGE_EMPTY_COLOR, cartridge_rect, width=4, border_radius=16)
        text_surface = font.render("Empty Slot", True, theme.CARTRIDGE_EMPTY_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=cartridge_rect.center)
        game_surface.blit(text_surface, text_rect)


def get_back_button_rect():
    return pygame.Rect(theme.MARGIN, theme.MARGIN, 140, 60)


def draw_subject_screen(subject_name, game_mouse_pos):
    game_surface.fill(theme.BG_COLOR)

    # Title
    title_surface = title_font.render(subject_name, True, theme.TEXT_COLOR)
    game_surface.blit(title_surface, (theme.MARGIN + 160, theme.MARGIN + 12))

    # Back button
    back_rect = get_back_button_rect()
    hovered = back_rect.collidepoint(game_mouse_pos)
    pygame.draw.rect(game_surface, theme.BACK_HOVER_COLOR if hovered else theme.BACK_COLOR, back_rect, border_radius=12)
    back_text = font.render("< Back", True, theme.TEXT_COLOR)
    back_text_rect = back_text.get_rect(center=back_rect.center)
    game_surface.blit(back_text, back_text_rect)

    # Activity tiles, shifted down to leave room for the title/back row
    activities = subjects[subject_name]
    top_offset = theme.MARGIN + 100
    act_grid_height = theme.GAME_HEIGHT - top_offset - theme.MARGIN
    act_tile_height = (act_grid_height - (theme.TILE_GAP * (theme.ROWS - 1))) // theme.ROWS

    for i, activity in enumerate(activities):
        rect = get_tile_rect(i, t_height=act_tile_height)
        rect.y += top_offset - theme.MARGIN  # shift down below the header
        hovered = rect.collidepoint(game_mouse_pos)
        draw_tile(rect, activity["label"], theme.TILE_COLOR, hovered)


def handle_home_click(pos):
    global current_screen
    for tile in home_tiles:
        if tile["rect"].collidepoint(pos):
            current_screen = tile["label"]
            return
    if cartridge_rect.collidepoint(pos):
        if cartridge_inserted():
            print("Cartridge clicked! (would launch cartridge content)")
        else:
            print("Cartridge slot clicked, but nothing is inserted.")


def handle_subject_click(subject_name, pos):
    global current_screen

    back_rect = get_back_button_rect()
    if back_rect.collidepoint(pos):
        current_screen = "home"
        return

    activities = subjects[subject_name]
    top_offset = theme.MARGIN + 100
    act_grid_height = theme.GAME_HEIGHT - top_offset - theme.MARGIN
    act_tile_height = (act_grid_height - (theme.TILE_GAP * (theme.ROWS - 1))) // theme.ROWS

    for i, activity in enumerate(activities):
        rect = get_tile_rect(i, t_height=act_tile_height)
        rect.y += top_offset - theme.MARGIN
        if rect.collidepoint(pos):
            print(f"{activity['label']} clicked! (would launch: {activity['command']})")
            return


# --- Main loop ---
clock = pygame.time.Clock()
running = True

while running:
    raw_mouse_pos = pygame.mouse.get_pos()
    mouse_pos = screen_to_game_pos(raw_mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game_pos = screen_to_game_pos(event.pos)
            if current_screen == "home":
                handle_home_click(game_pos)
            else:
                handle_subject_click(current_screen, game_pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_screen == "home":
                    running = False
                else:
                    current_screen = "home"

    if current_screen == "home":
        draw_home_screen(mouse_pos)
    else:
        draw_subject_screen(current_screen, mouse_pos)

    # --- Composite the game_surface onto the real screen, centered with black bars ---
    screen.fill((0, 0, 0))
    scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_width, scaled_height))
    screen.blit(scaled_surface, (offset_x, offset_y))
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
