"""
Tic-Tac-Toe-via-GitHub-Issues game engine.

Triggered by a GitHub Action on:
  - issues: opened      -> starts a new game if the issue has the 'tictactoe' label
  - issue_comment: created -> treats a coordinate comment as a player move

State is stored invisibly inside the issue body using an HTML comment,
so it never renders on GitHub but the bot can read it back via the API.
"""

import json
import os
import random
import re

from github import Github

# State regex matching board state (9 characters of '.', 'X', 'O') and turn count
STATE_RE = re.compile(
    r"<!--\s*TICTACTOE_STATE\s*board=(?P<board>[.XO]{9})\s*turn=(?P<turn>\d+)\s*-->",
    re.IGNORECASE,
)


def get_event():
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        return json.load(f)


def check_winner(board):
    winning_combos = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
        (0, 4, 8), (2, 4, 6)             # diagonals
    ]
    for combo in winning_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != '.':
            return board[combo[0]]
    return None


def get_bot_move(board):
    winning_combos = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
        (0, 4, 8), (2, 4, 6)             # diagonals
    ]
    
    # 1. Can we (O) win in this turn?
    for combo in winning_combos:
        vals = [board[i] for i in combo]
        if vals.count('O') == 2 and vals.count('.') == 1:
            return combo[vals.index('.')]

    # 2. Block the player (X) from winning?
    for combo in winning_combos:
        vals = [board[i] for i in combo]
        if vals.count('X') == 2 and vals.count('.') == 1:
            return combo[vals.index('.')]

    # 3. Take the center if available
    if board[4] == '.':
        return 4

    # 4. Take corners if available
    corners = [0, 2, 6, 8]
    available_corners = [c for c in corners if board[c] == '.']
    if available_corners:
        return random.choice(available_corners)

    # 5. Take any remaining cell
    available = [i for i, val in enumerate(board) if val == '.']
    if available:
        return random.choice(available)
        
    return None


def parse_move(move_str):
    cleaned = move_str.strip().lower()
    
    # Pattern 1: Letter (a-c) followed optionally by space/comma/dash, followed by number (1-3)
    # e.g., "A1", "a 2", "b,3", "c-1"
    match = re.search(r"\b([a-c])\s*[-,\s]?\s*([1-3])\b", cleaned)
    if match:
        row = ord(match.group(1)) - ord('a')
        col = int(match.group(2)) - 1
        return row, col
        
    # Pattern 2: Number (1-3) followed optionally by space/comma/dash, followed by number (1-3)
    # e.g., "1,2", "1 1", "3-3", "22"
    match = re.search(r"\b([1-3])\s*[-,\s]?\s*([1-3])\b", cleaned)
    if match:
        row = int(match.group(1)) - 1
        col = int(match.group(2)) - 1
        return row, col

    # Pattern 3: Number (1-3) followed by Letter (a-c), e.g., "1A", "3 c"
    match = re.search(r"\b([1-3])\s*([a-c])\b", cleaned)
    if match:
        col = int(match.group(1)) - 1
        row = ord(match.group(2)) - ord('a')
        return row, col
        
    return None


def render_body(board, turn):
    mapping = {
        'X': '❌',
        'O': '⭕',
        '.': '⬜'
    }
    
    winner = check_winner(board)
    won = (winner == 'X')
    lost = (winner == 'O')
    tie = (not won and not lost and '.' not in board)
    
    status = ""
    if won:
        status = "\n\n### 🎉 YOU WON! Congratulations! 🏆\n"
    elif lost:
        status = "\n\n### 💀 GAME OVER! The bot won. Better luck next time! 🤖\n"
    elif tie:
        status = "\n\n### 🤝 IT'S A TIE! Good game! 🤝\n"

    table = f"""
| | 1 | 2 | 3 |
|---|---|---|---|
| **A** | {mapping[board[0]]} | {mapping[board[1]]} | {mapping[board[2]]} |
| **B** | {mapping[board[3]]} | {mapping[board[4]]} | {mapping[board[5]]} |
| **C** | {mapping[board[6]]} | {mapping[board[7]]} | {mapping[board[8]]} |
"""

    body = f"""## 🎮 Tic-Tac-Toe

{table}

**Current Turn:** {turn}
**You:** ❌ (Player) | **Bot:** ⭕ (Computer)
{status}
---
### How to play:
Comment with coordinates (e.g. `B2`, `2,2`, or `A1`) to place your ❌.

<!-- TICTACTOE_STATE
board={''.join(board)}
turn={turn}
-->
"""
    return body, won, lost, tie


def parse_state(body):
    m = STATE_RE.search(body or "")
    if not m:
        return None
    board = list(m.group("board").upper())
    turn = int(m.group("turn"))
    return board, turn


def has_label(labels, name):
    return any(l.get("name") == name for l in labels)


def main():
    event = get_event()
    event_name = os.environ["GITHUB_EVENT_NAME"]
    token = os.environ["GITHUB_TOKEN"]
    repo_full_name = os.environ["GITHUB_REPOSITORY"]

    gh = Github(token)
    repo = gh.get_repo(repo_full_name)

    if event_name == "issues" and event["action"] == "opened":
        labels = event["issue"].get("labels", [])
        if not has_label(labels, "tictactoe"):
            return

        issue = repo.get_issue(event["issue"]["number"])
        board = list(".........")
        body, _, _, _ = render_body(board, 0)
        issue.edit(body=body)
        issue.create_comment("New game started! Comment with a coordinate (e.g., `A1` or `2,2`) to place your ❌. 🕹️")

    elif event_name == "issue_comment" and event["action"] == "created":
        labels = event["issue"].get("labels", [])
        if not has_label(labels, "tictactoe"):
            return
        if event["issue"]["state"] == "closed":
            return
        referee_identity = os.environ.get("REFEREE_IDENTITY", "github-actions[bot]")
        if event["comment"]["user"]["login"] == referee_identity:
            return

        issue = repo.get_issue(event["issue"]["number"])
        commenter = event["comment"]["user"]["login"]
        guess_raw = event["comment"]["body"].strip()

        state = parse_state(issue.body)
        if state is None:
            return
        board, turn = state

        move = parse_move(guess_raw)
        if move is None:
            issue.create_comment(
                f"@{commenter} I couldn't parse your move. Please comment with a coordinate like `A1`, `B2`, or `2,2`."
            )
            return

        row, col = move
        idx = row * 3 + col
        if board[idx] != '.':
            issue.create_comment(
                f"@{commenter} Cell at Row {chr(65 + row).upper()}, Column {col + 1} is already occupied! Try another cell."
            )
            return

        # Player move
        board[idx] = 'X'
        turn += 1

        # Check if player won or if it's a tie
        winner = check_winner(board)
        if winner == 'X':
            body, won, lost, tie = render_body(board, turn)
            issue.edit(body=body)
            issue.add_to_labels("won")
            issue.edit(state="closed")
            return

        if '.' not in board:
            body, won, lost, tie = render_body(board, turn)
            issue.edit(body=body)
            issue.add_to_labels("tied")
            issue.edit(state="closed")
            return

        # Bot move
        bot_idx = get_bot_move(board)
        if bot_idx is not None:
            board[bot_idx] = 'O'
            turn += 1

        # Re-evaluate after bot move
        body, won, lost, tie = render_body(board, turn)
        issue.edit(body=body)

        if lost:
            issue.add_to_labels("lost")
            issue.edit(state="closed")
        elif tie:
            issue.add_to_labels("tied")
            issue.edit(state="closed")


if __name__ == "__main__":
    main()
