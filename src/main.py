from chess_game import ChessGame
import chess
import random
import src.gui as gui # Import the gui module

def get_player_name_tui(turn, game_mode, player_color_choice=None):
    """Gets player name for Text User Interface"""
    if game_mode == "human" or player_color_choice is None:
        return "Player 1 (White)" if turn == chess.WHITE else "Player 2 (Black)"
    if turn == player_color_choice:
        return "You"
    else:
        return "AI"

def tui_game_loop(game: ChessGame, game_mode: str, player_color_choice: chess.Color = None):
    """Handles the Text-based User Interface game loop."""
    print("Starting Text-Based Chess Game!")
    ai_color = None
    if game_mode == "ai":
        ai_color = not player_color_choice

    while True:
        print("\n" + "="*20)
        print(game.get_board_display())
        print("="*20)

        status = game.get_game_status()
        print(f"Status: {status}")

        if status != "Ongoing":
            if status == "Checkmate":
                winner_is_player = False
                if game_mode == "ai":
                    winner_is_player = game.board.turn != ai_color
                    print(f"Checkmate! {'You win' if winner_is_player else 'AI wins'}!")
                else: # human vs human
                    winner_color_name = "Black" if game.board.turn == chess.WHITE else "White"
                    print(f"Checkmate! {winner_color_name} wins.")
            else:
                print(f"Game over: {status}")
            break

        current_turn_is_ai = game_mode == "ai" and game.board.turn == ai_color
        current_player_display_name = get_player_name_tui(game.board.turn, game_mode, player_color_choice)

        if current_turn_is_ai:
            print(f"{current_player_display_name}'s turn...")
            legal_moves = game.get_legal_moves()
            if not legal_moves:
                print("Error: AI has no legal moves but game is ongoing.")
                break

            # AI Improvement: Prefer Captures
            capturing_moves = []
            for move_uci_str in legal_moves:
                move_obj = game.board.parse_uci(move_uci_str)
                if game.board.is_capture(move_obj):
                    capturing_moves.append(move_uci_str)

            if capturing_moves:
                ai_move_uci = random.choice(capturing_moves)
                print("AI chose a capturing move.")
            else:
                ai_move_uci = random.choice(legal_moves)
                # print("AI chose a non-capturing move.") # Optional debug

            try:
                ai_move_san = game.board.san(game.board.parse_uci(ai_move_uci))
                print(f"AI plays: {ai_move_san}")
            except Exception:
                print(f"AI plays: {ai_move_uci} (SAN conversion failed)")
            game.make_move(ai_move_uci)
        else: # Player's turn
            while True:
                move_san = input(f"{current_player_display_name}, enter your move (e.g., e4, Nf3, O-O): ")
                try:
                    move_uci = game.board.parse_san(move_san).uci() # Converts SAN to UCI
                    # Check for promotion for player move (simple auto-queen)
                    from_piece = game.board.piece_at(game.board.parse_san(move_san).from_square)
                    if from_piece and from_piece.piece_type == chess.PAWN:
                        to_square = game.board.parse_san(move_san).to_square
                        if (from_piece.color == chess.WHITE and chess.square_rank(to_square) == 7) or \
                           (from_piece.color == chess.BLACK and chess.square_rank(to_square) == 0):
                            move_uci += 'q' # Auto-promote to queen

                    if game.make_move(move_uci):
                        break
                    else:
                        print("Invalid move. The move is not legal in the current position. Try again.")
                except chess.InvalidMoveError:
                    print("Invalid move format (not SAN). Try again.")
                except chess.IllegalMoveError:
                    print("Illegal move. This move is not allowed by chess rules. Try again.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}. Try again.")

def main():
    game = ChessGame()
    print("Welcome to Chess!")

    ui_choice = ""
    while ui_choice not in ["gui", "text"]:
        ui_choice = input("Choose interface: Graphical (gui) or Text-based (text): ").lower()

    game_mode = ""
    while game_mode not in ["human", "ai"]:
        game_mode = input("Play against another human or AI? (human/ai): ").lower()

    player_color_choice = chess.WHITE # Default, matters only for AI mode
    if game_mode == "ai":
        player_color_str = ""
        while player_color_str not in ["white", "black"]:
            player_color_str = input("Do you want to play as White or Black? (white/black): ").lower()
        player_color_choice = chess.WHITE if player_color_str == "white" else chess.BLACK
        ai_opponent_color_name = "Black" if player_color_choice == chess.WHITE else "White"
        print(f"You are playing as {player_color_str.capitalize()}. AI is {ai_opponent_color_name}.")

    if ui_choice == "gui":
        print("Starting GUI game...")
        # Ensure gui module is found, might need to adjust path if running from root vs src
        try:
            import src.gui as gui
            gui.run_gui_game(game, game_mode, player_color_choice)
        except ImportError:
             print("Error: Could not import the GUI module. Make sure it's in the 'src' directory.")
        except Exception as e:
            print(f"An error occurred while running the GUI: {e}")
            print("If it's a display error, ensure you have a display server (e.g., X11) running if not on a desktop.")

    else: # Text-based game
        tui_game_loop(game, game_mode, player_color_choice)

    print("Thanks for playing!")

if __name__ == "__main__":
    main()
