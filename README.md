# 🎮 Tic-Tac-Toe-as-a-GitHub-Issue

A tiny, self-contained game engine for Tic-Tac-Toe played inside GitHub Issues. The issue body is the live board, updated dynamically on every turn.

## How it works

- **New game:** Starts when an issue with the label `tictactoe` is opened.
- **Player moves:** Made by commenting coordinates on the issue (e.g., `B2`, `2,2`, `A1`).
- **Bot/Opponent moves:** The engine (playing as `⭕`) automatically responds and places its mark during the same turn.
- **Labels:** Updates labels to `won`, `lost`, or `tied` and closes the issue when the game ends.

## Setup

1. Copy this folder's contents (`.github/` and `scripts/`) into your repository.
2. Enable GitHub Actions for your repository (Settings → Actions → General) and grant them write permissions for issues.
3. To start a game:
   - **Humans:** Go to **Issues → New Issue → 🎮 New Tic-Tac-Toe Game**.
   - **AI Agents / Programmatic Play:** Call the GitHub Issues API directly to create an issue with the label `tictactoe`:
     ```bash
     curl -X POST \
       -H "Authorization: token YOUR_GITHUB_TOKEN" \
       -H "Accept: application/vnd.github.v3+json" \
       https://api.github.com/repos/YOUR_OWNER/YOUR_REPO/issues \
       -d '{"title": "Tic-Tac-Toe Game", "labels": ["tictactoe"]}'
     ```
4. Comment a coordinate to make a move. The bot will automatically respond and update the issue body.

## Turn-Taking Rules

- You play as `❌`. The computer opponent plays as `⭕`.
- The game is turn-based. Once you comment a valid empty coordinate, the engine validates the move, registers it, executes its own move, updates the board, and writes the state.
- **No Bot Exclusion:** legitimate AI-agent players can play by commenting via the API. Only the referee engine itself (`github-actions[bot]`) is ignored to prevent feedback loops.

## State and Security Caveats

The game board state is stored inside the issue body as a hidden HTML comment:
```html
<!-- TICTACTOE_STATE
board=.........
turn=0
-->
```
- **Caveat:** This state block is technically readable by fetching the issue body via the GitHub API or clicking "raw" on the issue UI. For Tic-Tac-Toe, all board positions are public anyway, so this does not impact gameplay fairness.
