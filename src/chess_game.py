import chess

class ChessGame:
    def __init__(self):
        self.board = chess.Board()

    def make_move(self, move_uci: str) -> bool:
        try:
            move = self.board.parse_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            return False
        except ValueError:
            return False

    def get_board_display(self) -> str:
        return str(self.board)

    def get_game_status(self) -> str:
        if self.board.is_checkmate():
            return "Checkmate"
        if self.board.is_stalemate():
            return "Stalemate"
        if self.board.is_insufficient_material():
            return "Draw by insufficient material"
        if self.board.is_seventyfive_moves():
            return "Draw by seventyfive moves rule"
        if self.board.is_fivefold_repetition():
            return "Draw by fivefold repetition"
        return "Ongoing"

    def get_legal_moves(self) -> list[str]:
        return [move.uci() for move in self.board.legal_moves]

    def get_move_history_san(self) -> list[str]:
        """Returns the game's move history in Standard Algebraic Notation (SAN)."""
        history_san = []
        # Need a temporary board to replay moves for SAN generation,
        # as board.san() requires the move to be legal in the current position.
        temp_board = self.board.copy()

        # Unwind moves from the main board's stack to get them in order
        # and then replay on temp_board to generate SAN
        moves_to_replay = []
        while temp_board.move_stack:
            moves_to_replay.append(temp_board.pop())
        moves_to_replay.reverse() # Now moves are in chronological order

        # Replay on a fresh board
        fresh_board = chess.Board()
        for move in moves_to_replay:
            move_color = fresh_board.turn # Whose turn it IS before the move
            san_move = fresh_board.san(move) # Get SAN for the move about to be made

            if move_color == chess.WHITE:
                history_san.append(f"{fresh_board.fullmove_number}. {san_move}")
            else: # Black's move
                if not history_san: # Should not happen if white moved first
                    history_san.append(f"... {san_move}") # Or handle error
                else:
                    history_san[-1] += f" {san_move}"

            fresh_board.push(move) # Make the move

        return history_san
