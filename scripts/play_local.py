#!/usr/bin/env python3
"""
Interactive CLI for playing Tic-Tac-Toe locally.
Imports game rules and AI moves from scripts/tictactoe.py.
"""

import sys
import os
import time

# Ensure the scripts directory is in the path to import tictactoe
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tictactoe import check_winner, get_bot_move, parse_move
except ImportError:
    print("Error: Could not import tictactoe.py. Make sure scripts/tictactoe.py exists.")
    sys.exit(1)


def print_board(board):
    mapping = {
        'X': '\033[91m❌\033[0m',  # Red X
        'O': '\033[94m⭕\033[0m',  # Blue O
        '.': '⬜'                  # White square
    }
    
    print("\n      1   2   3")
    print("   ┌───┬───┬───┐")
    print(f" A │ {mapping[board[0]]} │ {mapping[board[1]]} │ {mapping[board[2]]} │")
    print("   ├───┼───┼───┤")
    print(f" B │ {mapping[board[3]]} │ {mapping[board[4]]} │ {mapping[board[5]]} │")
    print("   ├───┼───┼───┤")
    print(f" C │ {mapping[board[6]]} │ {mapping[board[7]]} │ {mapping[board[8]]} │")
    print("   └───┴───┴───┘\n")


def main():
    print("=" * 45)
    print("🎮  Welcome to Local Tic-Tac-Toe!  🎮")
    print("=" * 45)
    print("You play as \033[91m❌\033[0m (Player). The bot plays as \033[94m⭕\033[0m (Computer).")
    print("Enter coordinates (e.g. A1, B2, 2,2) to make a move.")
    print("Type 'exit' or 'quit' to end the game.\n")

    board = list(".........")
    print_board(board)

    while True:
        # Player Move
        try:
            move_str = input("\033[92mYour move (e.g., A1): \033[0m").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGame exited. Goodbye!")
            break

        if move_str.lower() in ('exit', 'quit'):
            print("Game exited. Goodbye!")
            break

        move = parse_move(move_str)
        if move is None:
            print("\033[93m⚠️  Invalid coordinates! Try A1, B2, 1,2, etc.\033[0m")
            continue

        row, col = move
        idx = row * 3 + col
        if board[idx] != '.':
            print("\033[93m⚠️  That cell is already occupied! Choose an empty one.\033[0m")
            continue

        # Place player mark
        board[idx] = 'X'
        print_board(board)

        # Check Player Win
        winner = check_winner(board)
        if winner == 'X':
            print("🎉 \033[92mCONGRATULATIONS! You won! 🏆\033[0m\n")
            break

        if '.' not in board:
            print("🤝 \033[93mIT'S A TIE! Good game! 🤝\033[0m\n")
            break

        # Bot Move
        print("🤖 Bot is thinking...")
        time.sleep(0.6)
        
        bot_idx = get_bot_move(board)
        if bot_idx is not None:
            board[bot_idx] = 'O'
            print(f"🤖 Bot played at cell {chr(65 + (bot_idx // 3))}{1 + (bot_idx % 3)}:")
            print_board(board)

        # Check Bot Win
        winner = check_winner(board)
        if winner == 'O':
            print("💀 \033[91mGAME OVER! The bot won. Better luck next time! 🤖\033[0m\n")
            break

        if '.' not in board:
            print("🤝 \033[93mIT'S A TIE! Good game! 🤝\033[0m\n")
            break


if __name__ == "__main__":
    main()
