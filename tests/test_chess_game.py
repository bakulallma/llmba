import unittest
import sys
import os

# Adjust path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chess_game import ChessGame
from chess import Board, Move, KING, PAWN, KNIGHT # For setting up test scenarios

class TestChessGame(unittest.TestCase):

    def setUp(self):
        """Set up a new ChessGame instance for each test."""
        self.game = ChessGame()

    def test_initialization_and_board_display(self):
        self.assertIsNotNone(self.game.board, "Board should be initialized.")
        self.assertEqual(self.game.board.fen(), Board().fen(), "New game should have a standard starting position.")
        self.assertTrue(len(self.game.get_board_display()) > 0, "Board display string should not be empty.")

    def test_make_legal_move(self):
        initial_fen = self.game.board.fen()
        move_uci = "e2e4" # A legal opening move
        self.assertTrue(self.game.make_move(move_uci), "make_move should return True for a legal move.")
        self.assertNotEqual(self.game.board.fen(), initial_fen, "Board state should change after a legal move.")
        # Check if the specific move was made (e4 pawn is now on e4)
        self.assertIsNotNone(self.game.board.piece_at(chess.E4), "Pawn should be at e4 after e2e4.")
        self.assertIsNone(self.game.board.piece_at(chess.E2), "E2 should be empty after e2e4.")


    def test_make_illegal_move_pawn_backward(self):
        self.game.make_move("e2e4") # Make one legal move
        initial_fen = self.game.board.fen()
        # Try to move e-pawn backward (illegal)
        self.assertFalse(self.game.make_move("e4e2"), "make_move should return False for an illegal move (pawn backward).")
        self.assertEqual(self.game.board.fen(), initial_fen, "Board state should not change after an illegal move.")

    def test_make_illegal_move_wrong_piece(self):
        # Try to move a non-existent piece or opponent's piece
        initial_fen = self.game.board.fen()
        self.assertFalse(self.game.make_move("e7e5"), "make_move should return False for moving opponent's piece (as white).")
        self.assertEqual(self.game.board.fen(), initial_fen, "Board state should not change.")

    def test_make_move_that_puts_king_in_check(self):
        # Setup: e.g. White: Ke1, Qe2. Black: ke8. Move Qe2-e7+
        self.game.board = Board(fen=None) # Clear board
        self.game.board.set_piece_at(chess.E1, chess.Piece(KING, chess.WHITE))
        self.game.board.set_piece_at(chess.E2, chess.Piece(chess.QUEEN, chess.WHITE))
        self.game.board.set_piece_at(chess.E8, chess.Piece(KING, chess.BLACK))
        self.game.board.turn = chess.WHITE

        self.assertTrue(self.game.make_move("e2e7"), "Moving queen to e7 should be legal.")
        self.assertTrue(self.game.board.is_check(), "Black king should be in check.")

    def test_get_legal_moves_initial_position(self):
        legal_moves = self.game.get_legal_moves()
        self.assertTrue(len(legal_moves) > 0, "There should be legal moves at the start.")
        self.assertIn("g1f3", legal_moves, "Nf3 should be a legal move.") # Knight opening
        self.assertIn("e2e4", legal_moves, "e4 should be a legal move.")   # Pawn opening
        self.assertEqual(len(legal_moves), 20, "Standard starting position has 20 legal moves.")


    def test_get_legal_moves_limited_scenario(self):
        # King trapped by own pieces, only one pawn move possible
        # . . . . k . . .
        # . . . . P . . . (black pawn)
        # . . . P K P . . (white pieces)
        self.game.board = Board(fen=None)
        self.game.board.set_piece_at(chess.E8, chess.Piece(KING, chess.BLACK))
        self.game.board.set_piece_at(chess.E7, chess.Piece(PAWN, chess.BLACK))
        self.game.board.set_piece_at(chess.D6, chess.Piece(PAWN, chess.WHITE))
        self.game.board.set_piece_at(chess.E6, chess.Piece(KING, chess.WHITE))
        self.game.board.set_piece_at(chess.F6, chess.Piece(PAWN, chess.WHITE))
        self.game.board.turn = chess.BLACK # Black's turn

        legal_moves = self.game.get_legal_moves()
        self.assertIn("e7e6", legal_moves, "Black pawn e7e6 should be legal.")
        self.assertEqual(len(legal_moves), 1, "Only one legal move (pawn e7e6) for black.")


    def test_get_game_status_ongoing(self):
        self.assertEqual(self.game.get_game_status(), "Ongoing", "Initial game status should be Ongoing.")

    def test_get_game_status_checkmate_fools_mate(self):
        # Fool's Mate: 1. f3 e5 2. g4 Qh4#
        self.assertTrue(self.game.make_move("f2f3"))
        self.assertTrue(self.game.make_move("e7e5"))
        self.assertTrue(self.game.make_move("g2g4"))
        self.assertTrue(self.game.make_move("d8h4")) # Qh4#
        self.assertEqual(self.game.get_game_status(), "Checkmate", "Status should be Checkmate.")
        self.assertTrue(self.game.board.is_checkmate(), "Board confirms checkmate.")

    def test_get_game_status_stalemate(self):
        # King to h1, Queen to f2, Opponent king to h3. White to move. Qh2 is stalemate.
        # . . . . . . . k (bKh8)
        # . . . . . Q . . (wQf7)
        # . . . . . . . K (wKh6)
        # Black to move, only Kh8-g7, then White Qf7-g6. Black Kg7-h8. White Qg6-f6. Black Kh8-g7. White Kh6-g5. Black Kg7-h8. White Qf6-h4. Black Kh8-g7. White Qh4-h5. Black Kg7-h8. White Qh5-g4. Black Kh8-g7. White Qg4-g2. Black Kg7-h8 (stalemate)
        # More direct stalemate: White: Ka1, Qc2. Black: Kc3. White to move. No legal moves for black if white plays Qb2.
        # Simpler: White: Kh8, Black: Kf6, Pf7. White to move. White has no moves.
        self.game.board = Board(fen=None)
        self.game.board.set_piece_at(chess.H8, chess.Piece(KING, chess.WHITE))
        self.game.board.set_piece_at(chess.F6, chess.Piece(KING, chess.BLACK))
        self.game.board.set_piece_at(chess.F7, chess.Piece(PAWN, chess.BLACK)) # Black pawn blocks black king
        self.game.board.turn = chess.WHITE # White to move
        # White king has no moves (g8, g7, h7 controlled by Kf6 or Pf7)
        self.assertEqual(self.game.get_game_status(), "Stalemate", "Status should be Stalemate.")
        self.assertTrue(self.game.board.is_stalemate(), "Board confirms stalemate.")


    def test_get_game_status_draw_insufficient_material_kvk(self):
        self.game.board = Board(fen=None) # Clear board
        self.game.board.set_piece_at(chess.E1, chess.Piece(KING, chess.WHITE))
        self.game.board.set_piece_at(chess.E8, chess.Piece(KING, chess.BLACK))
        self.assertEqual(self.game.get_game_status(), "Draw by insufficient material", "Status should be Draw by insufficient material (K vs K).")
        self.assertTrue(self.game.board.is_insufficient_material(), "Board confirms insufficient material.")

    def test_get_game_status_draw_insufficient_material_kvkn(self):
        self.game.board = Board(fen=None) # Clear board
        self.game.board.set_piece_at(chess.E1, chess.Piece(KING, chess.WHITE))
        self.game.board.set_piece_at(chess.E8, chess.Piece(KING, chess.BLACK))
        self.game.board.set_piece_at(chess.D8, chess.Piece(KNIGHT, chess.BLACK))
        self.assertEqual(self.game.get_game_status(), "Draw by insufficient material", "Status should be Draw by insufficient material (K vs KN).")
        self.assertTrue(self.game.board.is_insufficient_material(), "Board confirms insufficient material for K vs KN.")

    # Seventyfive moves and fivefold repetition are harder to unit test concisely
    # as they require playing out many moves. These are typically covered by python-chess library itself.

if __name__ == '__main__':
    unittest.main()
