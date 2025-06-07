import pygame as pg
import os

# Initialize Pygame font module
pg.init()
pg.font.init()

# Define piece names and colors
pieces = {
    'P': 'Pawn', 'N': 'Knight', 'B': 'Bishop', 'R': 'Rook', 'Q': 'Queen', 'K': 'King'
}
colors = {
    'w': (255, 255, 255),  # White
    'b': (0, 0, 0)        # Black
}
bg_colors = {
    'w': (100, 100, 100), # Background for white pieces (grey)
    'b': (200, 200, 200)  # Background for black pieces (light grey)
}


square_size = 60  # Image size
font_size = 40
try:
    font = pg.font.SysFont(None, font_size) # Use default system font
except Exception as e:
    print(f"Could not load system font, using Pygame default font. Error: {e}")
    font = pg.font.Font(None, font_size) # Pygame's default font


output_dir = "assets/pieces"
os.makedirs(output_dir, exist_ok=True)

for color_code, piece_color_rgb in colors.items():
    for piece_symbol, piece_name in pieces.items():
        filename = os.path.join(output_dir, f"{color_code}{piece_symbol}.png")

        surface = pg.Surface((square_size, square_size), pg.SRCALPHA) # Use SRCALPHA for transparency
        surface.fill((0,0,0,0)) # Fill with transparent background initially

        # Draw a circle as a background for the text, to make it more piece-like
        circle_radius = square_size // 2
        circle_bg = bg_colors[color_code]
        pg.draw.circle(surface, circle_bg, (circle_radius, circle_radius), circle_radius)

        # Create text render
        text_surface = font.render(piece_symbol, True, piece_color_rgb)
        text_rect = text_surface.get_rect(center=(square_size // 2, square_size // 2))

        surface.blit(text_surface, text_rect)

        try:
            pg.image.save(surface, filename)
            print(f"Saved {filename}")
        except Exception as e:
            print(f"Failed to save {filename}: {e}")

pg.quit()
