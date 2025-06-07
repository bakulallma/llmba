import pygame as pg
import chess
import os
import random # For AI
from chess_game import ChessGame # Import ChessGame

# --- Constants ---
BOARD_WIDTH = 480  # Was SCREEN_WIDTH
BOARD_HEIGHT = 480 # Was SCREEN_HEIGHT
SQUARE_SIZE = BOARD_WIDTH // 8

HISTORY_WIDTH = 200
INFO_HEIGHT = 40

SCREEN_WIDTH = BOARD_WIDTH + HISTORY_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT + INFO_HEIGHT # Renamed from TOTAL_HEIGHT for clarity

# Colors
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
HIGHLIGHT_COLOR = (255, 255, 51, 150)
LEGAL_MOVE_HIGHLIGHT_COLOR = (0, 255, 0, 100)
HISTORY_BG_COLOR = (200, 200, 200) # Light grey for history panel
HISTORY_TEXT_COLOR = (0, 0, 0)

# --- Asset Loading & Font ---
PIECE_IMAGES = {}
INFO_FONT = None
HISTORY_FONT = None

def init_pygame_essentials():
    global INFO_FONT, HISTORY_FONT
    pg.init()
    pg.font.init()
    try:
        INFO_FONT = pg.font.SysFont(None, 30)
        HISTORY_FONT = pg.font.SysFont(None, 24) # Smaller font for history
    except Exception as e:
        print(f"SysFont not found: {e}, using default font.")
        INFO_FONT = pg.font.Font(None, 30)
        HISTORY_FONT = pg.font.Font(None, 24)
    load_piece_images()

def load_piece_images():
    # ... (load_piece_images implementation remains the same)
    pieces_symbols = ['P', 'N', 'B', 'R', 'Q', 'K']
    colors = ['w', 'b']
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'pieces')

    for color in colors:
        for symbol in pieces_symbols:
            filename = f"{color}{symbol}.png"
            path = os.path.join(base_path, filename)
            try:
                image = pg.image.load(path)
                image = pg.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                PIECE_IMAGES[f"{color}{symbol}"] = image
            except pg.error as e:
                print(f"Error loading piece image {path}: {e}")
    if not PIECE_IMAGES:
        print("CRITICAL: No piece images were loaded. Check asset path and files.")
    else:
        print(f"Loaded {len(PIECE_IMAGES)} piece images from {base_path}")


# --- Drawing Functions ---
def get_piece_symbol_from_chess_piece(piece: chess.Piece):
    # ... (remains the same)
    color = 'w' if piece.color == chess.WHITE else 'b'
    symbol = piece.symbol().upper()
    return f"{color}{symbol}"

def draw_board_and_pieces(screen, game: ChessGame, selected_square_idx=None, legal_moves_for_selected=[]):
    # Draws only the 8x8 board and pieces, not the whole screen
    board_surface = screen.subsurface(pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT))
    for rank_idx in range(8):
        for file_idx in range(8):
            square_color = LIGHT_SQUARE if (rank_idx + file_idx) % 2 == 0 else DARK_SQUARE
            pg.draw.rect(board_surface, square_color, (file_idx * SQUARE_SIZE, rank_idx * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            current_square_chess_idx = chess.square(file_idx, 7 - rank_idx)

            if selected_square_idx is not None and current_square_chess_idx == selected_square_idx:
                s = pg.Surface((SQUARE_SIZE, SQUARE_SIZE), pg.SRCALPHA)
                s.fill(HIGHLIGHT_COLOR)
                board_surface.blit(s, (file_idx * SQUARE_SIZE, rank_idx * SQUARE_SIZE))

            if current_square_chess_idx in legal_moves_for_selected:
                s = pg.Surface((SQUARE_SIZE, SQUARE_SIZE), pg.SRCALPHA)
                pg.draw.circle(s, LEGAL_MOVE_HIGHLIGHT_COLOR, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//4)
                board_surface.blit(s, (file_idx * SQUARE_SIZE, rank_idx * SQUARE_SIZE))

            piece = game.board.piece_at(current_square_chess_idx)
            if piece:
                piece_img_key = get_piece_symbol_from_chess_piece(piece)
                if piece_img_key in PIECE_IMAGES:
                    board_surface.blit(PIECE_IMAGES[piece_img_key], (file_idx * SQUARE_SIZE, rank_idx * SQUARE_SIZE))

def draw_info_bar(screen, game: ChessGame):
    # Draws the info/status message bar below the board
    info_bar_rect = pg.Rect(0, BOARD_HEIGHT, BOARD_WIDTH, INFO_HEIGHT) # Spans only board width now
    pg.draw.rect(screen, BLACK_COLOR, info_bar_rect)

    status_text = game.get_game_status()
    turn_text = ""
    if status_text == "Ongoing":
        turn_text = "White's Turn" if game.board.turn == chess.WHITE else "Black's Turn"
        if game.board.is_check():
            status_text = f"Check! {turn_text}"
        else:
            status_text = turn_text
    elif status_text == "Checkmate":
        winner_color = "Black" if game.board.turn == chess.WHITE else "White" # Loser's turn when checkmated
        status_text = f"Checkmate! {winner_color} wins."
    elif status_text == "Stalemate" or "Draw by" in status_text:
         status_text = f"Draw: {status_text}"

    if INFO_FONT:
        text_surface = INFO_FONT.render(status_text, True, WHITE_COLOR)
        text_rect = text_surface.get_rect(center=info_bar_rect.center)
        screen.blit(text_surface, text_rect)

def draw_move_history(screen, game: ChessGame):
    history_panel_rect = pg.Rect(BOARD_WIDTH, 0, HISTORY_WIDTH, SCREEN_HEIGHT) # Full height next to board
    pg.draw.rect(screen, HISTORY_BG_COLOR, history_panel_rect)

    if not HISTORY_FONT: return

    move_history_san = game.get_move_history_san()

    padding = 5
    line_height = HISTORY_FONT.get_linesize()
    max_lines = (SCREEN_HEIGHT - 2 * padding) // line_height

    start_index = 0
    if len(move_history_san) > max_lines:
        start_index = len(move_history_san) - max_lines

    for i, move_str in enumerate(move_history_san[start_index:]):
        text_surface = HISTORY_FONT.render(move_str, True, HISTORY_TEXT_COLOR)
        screen.blit(text_surface, (BOARD_WIDTH + padding, padding + i * line_height))

def draw_everything(screen, game: ChessGame, selected_square_idx=None, legal_moves_for_selected=[]):
    screen.fill(BLACK_COLOR) # Fill whole background
    draw_board_and_pieces(screen, game, selected_square_idx, legal_moves_for_selected)
    draw_info_bar(screen, game)
    draw_move_history(screen, game)
    pg.display.flip()


# --- Main GUI Game Function ---
def run_gui_game(game: ChessGame, game_mode: str, player_color_choice: chess.Color = chess.WHITE):
    init_pygame_essentials()
    if not PIECE_IMAGES: return

    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Use new SCREEN_WIDTH, SCREEN_HEIGHT
    ai_color = None
    if game_mode == "ai":
        ai_color = not player_color_choice

    selected_square_idx = None
    running = True
    clock = pg.time.Clock()

    while running:
        current_player_turn = game.board.turn
        # Window caption now only shows generic title, turn is in info bar
        pg.display.set_caption(f"Chess Game")

        legal_moves_for_display = []
        # ... (rest of the legal_moves_for_display logic remains the same)
        if selected_square_idx is not None:
            piece = game.board.piece_at(selected_square_idx)
            if piece and piece.color == current_player_turn:
                for move_obj in game.board.legal_moves:
                    if move_obj.from_square == selected_square_idx:
                        legal_moves_for_display.append(move_obj.to_square)
            else:
                selected_square_idx = None

        # AI's turn logic (remains the same)
        if game_mode == "ai" and current_player_turn == ai_color and game.get_game_status() == "Ongoing":
            # ... (AI logic as previously updated)
            print("AI's turn...")
            legal_uci_moves = game.get_legal_moves()
            if legal_uci_moves:
                capturing_moves = []
                for move_uci_str in legal_uci_moves:
                    move_obj = game.board.parse_uci(move_uci_str)
                    if game.board.is_capture(move_obj):
                        capturing_moves.append(move_uci_str)

                if capturing_moves:
                    ai_move_uci = random.choice(capturing_moves)
                    print("AI (GUI) chose a capturing move.")
                else:
                    ai_move_uci = random.choice(legal_uci_moves)

                try:
                    ai_move_san = game.board.san(game.board.parse_uci(ai_move_uci))
                    print(f"AI plays: {ai_move_san} ({ai_move_uci})")
                except Exception:
                    print(f"AI plays: {ai_move_uci} (SAN conversion failed)")

                game.make_move(ai_move_uci)
                selected_square_idx = None
            else:
                print("AI has no legal moves.")
            pg.time.wait(500)


        # Event handling (remains mostly the same)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            is_player_turn = True
            if game_mode == "ai" and current_player_turn == ai_color:
                is_player_turn = False

            if is_player_turn and event.type == pg.MOUSEBUTTONDOWN and game.get_game_status() == "Ongoing":
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if mouse_y >= BOARD_HEIGHT or mouse_x >= BOARD_WIDTH : # Click outside board area
                        selected_square_idx = None # Deselect if clicking outside board
                        continue

                    file_clicked = mouse_x // SQUARE_SIZE
                    rank_clicked = mouse_y // SQUARE_SIZE
                    square_clicked_idx = chess.square(file_clicked, 7 - rank_clicked)

                    piece_on_clicked_square = game.board.piece_at(square_clicked_idx)

                    if selected_square_idx is None:
                        if piece_on_clicked_square and piece_on_clicked_square.color == current_player_turn:
                            selected_square_idx = square_clicked_idx
                    else:
                        move_uci = chess.Move(selected_square_idx, square_clicked_idx).uci()

                        from_piece = game.board.piece_at(selected_square_idx)
                        if from_piece and from_piece.piece_type == chess.PAWN:
                            is_white_promotion = (from_piece.color == chess.WHITE and chess.square_rank(square_clicked_idx) == 7)
                            is_black_promotion = (from_piece.color == chess.BLACK and chess.square_rank(square_clicked_idx) == 0)
                            if is_white_promotion or is_black_promotion:
                                move_uci += 'q'

                        if game.make_move(move_uci):
                            selected_square_idx = None
                        elif piece_on_clicked_square and piece_on_clicked_square.color == current_player_turn:
                            selected_square_idx = square_clicked_idx
                        else:
                            print(f"Illegal move: {move_uci}")
                            selected_square_idx = None

        # Draw all elements
        draw_everything(screen, game, selected_square_idx, legal_moves_for_display)

        current_game_status = game.get_game_status()
        if current_game_status != "Ongoing":
            # Prepare final message based on status
            final_message_display = current_game_status
            if current_game_status == "Checkmate":
                winner_color = "Black" if game.board.turn == chess.WHITE else "White"
                final_message_display = f"Checkmate! {winner_color} wins."
            elif current_game_status == "Stalemate" or "Draw by" in current_game_status:
                final_message_display = f"Draw: {current_game_status}"

            # Re-call draw_everything to ensure the final board state and message are displayed
            # The info bar within draw_everything will use the latest game status.
            draw_everything(screen, game, None, [])
            print(f"Game Over: {final_message_display}")
            pg.time.wait(3000)
            running = False

        clock.tick(30)

    pg.quit()

if __name__ == '__main__':
    print("Running gui.py directly for testing...")
    game_instance = ChessGame()
    run_gui_game(game_instance, "human", chess.WHITE)
    print("Finished test run of gui.py.")
