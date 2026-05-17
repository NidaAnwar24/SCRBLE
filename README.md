# 🎯 Scrble — Word Strategy Game

A mobile-first Scrabble-style word game built with Python + Kivy.  
Supports **2–6 players** (human or AI), played offline on one phone.

---

## 📁 Project Structure

```
scrble/
├── main.py                  ← Entry point — run this
├── requirements.txt
├── buildozer.spec           ← For Android packaging
├── game/
│   ├── __init__.py
│   └── engine.py            ← All game logic (board, tiles, scoring, AI)
├── screens/
│   ├── __init__.py
│   ├── home_screen.py       ← Player setup screen
│   └── game_screen.py       ← Main game board screen
└── data/
    ├── __init__.py
    └── words.py             ← Valid word dictionary
```

---

## 🚀 Running on Desktop (for testing)

### 1. Install Python 3.10+

### 2. Install Kivy
```bash
pip install kivy[base]
```
On Windows you may also need:
```bash
pip install kivy[full]
```

### 3. Run the game
```bash
cd scrble
python main.py
```

This opens a **390×844 window** (mobile proportions) on your desktop for testing.

---

## 📱 Building for Android

### Prerequisites
- Linux or WSL2 (Windows Subsystem for Linux)
- Python 3.10
- Java 17

### Steps
```bash
pip install buildozer cython
cd scrble
buildozer android debug
```

The APK will appear at:
```
scrble/bin/Scrble-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

Install on your Android phone via:
```bash
buildozer android deploy run
```
Or copy the APK to your phone and install it directly.

---

## 🎮 How to Play

### Setup
1. Launch the app → **Home screen** appears
2. Choose **2–6 players** using the number buttons
3. Enter each player's name
4. Toggle any player to **🤖 AI** — they will play automatically
5. Tap **▶ START GAME**

### Gameplay (hot-seat — players pass the phone)
- **Select a tile** from your rack (bottom row) — it highlights gold
- **Tap a board square** to place it
- **Tap a placed tile** (amber) to recall it back to your rack
- When your word is complete, tap **✓ PLAY**
- The game validates the word and awards points

### Actions
| Button | Action |
|--------|--------|
| ✓ PLAY | Submit your word |
| ↩ RECALL | Take all tiles back to rack |
| PASS | Skip your turn |
| ⇄ SWAP | Exchange selected tiles with the bag |

### Scoring
| Premium Square | Bonus |
|----------------|-------|
| 🔴 TW (Triple Word) | ×3 word score |
| 🟠 DW (Double Word) | ×2 word score |
| 🔵 TL (Triple Letter) | ×3 letter value |
| 🔵 DL (Double Letter) | ×2 letter value |
| ★ Center | ×2 on first move |
| All 7 tiles played | +50 bonus (Bingo!) |

### Rules
- First word **must cover the center ★** square
- All words must connect to existing tiles
- Tiles must be placed in a straight line
- All words formed (including cross-words) must be valid
- Game ends when a player uses all tiles (bag empty) or all players pass twice

---

## 🤖 AI Player
- AI automatically searches for valid words from its rack
- Picks the highest-scoring valid placement it finds
- Passes if no valid word found
- AI turns happen automatically with a short delay

---

## 🛠 Extending the Game

### Add more words
Edit `data/words.py` — add words to the `VALID_WORDS` string.

### Change AI difficulty
In `game/engine.py` → `AIPlayer.find_move()`:
- Increase `min(200, ...)` to search more words (smarter but slower)
- Add `best_score` threshold for "easy" AI

### Change board size
Edit `BOARD_SIZE` in `game/engine.py` (default: 15×15).
