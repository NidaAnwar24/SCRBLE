"""
Scrble - Core Game Logic
Board setup, tile management, scoring, turn control
"""

import random
from data.words import is_valid_word

# ── Board Constants ──────────────────────────────────────────────────────────
BOARD_SIZE = 15
CENTER = (7, 7)

# Premium square types: TW=triple word, DW=double word, TL=triple letter, DL=double letter
PREMIUM_SQUARES = {}

def _setup_premium_squares():
    """Define all premium squares on the board"""
    tw = [(0,0),(0,7),(0,14),(7,0),(7,14),(14,0),(14,7),(14,14)]
    dw = [(1,1),(2,2),(3,3),(4,4),(1,13),(2,12),(3,11),(4,10),
          (10,4),(11,3),(12,2),(13,1),(10,10),(11,11),(12,12),(13,13)]
    tl = [(1,5),(1,9),(5,1),(5,5),(5,9),(5,13),(9,1),(9,5),(9,9),
          (9,13),(13,5),(13,9)]
    dl = [(0,3),(0,11),(2,6),(2,8),(3,0),(3,7),(3,14),(6,2),(6,6),
          (6,8),(6,12),(7,3),(7,11),(8,2),(8,6),(8,8),(8,12),
          (11,0),(11,7),(11,14),(12,6),(12,8),(14,3),(14,11)]
    for r, c in tw:
        PREMIUM_SQUARES[(r, c)] = 'TW'
    for r, c in dw:
        PREMIUM_SQUARES[(r, c)] = 'DW'
    for r, c in tl:
        PREMIUM_SQUARES[(r, c)] = 'TL'
    for r, c in dl:
        PREMIUM_SQUARES[(r, c)] = 'DL'
    PREMIUM_SQUARES[CENTER] = 'DW'  # center star

_setup_premium_squares()

# ── Tile Values ───────────────────────────────────────────────────────────────
TILE_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
    'Y': 4, 'Z': 10, '_': 0  # _ = blank tile
}

# Tile distribution (counts)
TILE_DISTRIBUTION = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3, 'H': 2,
    'I': 9, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2,
    'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1,
    'Y': 2, 'Z': 1, '_': 2
}

# ── Tile Bag ──────────────────────────────────────────────────────────────────
class TileBag:
    def __init__(self):
        self.tiles = []
        for letter, count in TILE_DISTRIBUTION.items():
            self.tiles.extend([letter] * count)
        random.shuffle(self.tiles)

    def draw(self, n=1):
        drawn = []
        for _ in range(n):
            if self.tiles:
                drawn.append(self.tiles.pop())
        return drawn

    def swap(self, tiles_to_return):
        """Swap tiles back and draw new ones"""
        if len(self.tiles) < len(tiles_to_return):
            return None
        drawn = self.draw(len(tiles_to_return))
        self.tiles.extend(tiles_to_return)
        random.shuffle(self.tiles)
        return drawn

    def remaining(self):
        return len(self.tiles)

# ── Board ─────────────────────────────────────────────────────────────────────
class Board:
    def __init__(self):
        self.grid = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.is_first_move = True

    def place_tile(self, row, col, letter):
        self.grid[row][col] = letter

    def remove_tile(self, row, col):
        letter = self.grid[row][col]
        self.grid[row][col] = None
        return letter

    def get_tile(self, row, col):
        return self.grid[row][col]

    def is_empty(self, row, col):
        return self.grid[row][col] is None

    def is_connected(self, placements):
        """Check if placed tiles connect to existing tiles or center"""
        if self.is_first_move:
            # First move must cover center
            return any(r == 7 and c == 7 for r, c, _ in placements)
        # Must connect to at least one existing tile
        for r, c, _ in placements:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if self.grid[nr][nc] is not None:
                        # Check it's not one of the newly placed tiles
                        if not any(pr == nr and pc == nc for pr, pc, _ in placements):
                            return True
        return False

    def get_words_from_placements(self, placements):
        """Extract all words formed by the placements"""
        temp_grid = [row[:] for row in self.grid]
        for r, c, letter in placements:
            temp_grid[r][c] = letter

        placement_set = {(r, c) for r, c, _ in placements}
        words = []

        # Check horizontal words
        checked_h = set()
        for r, c, _ in placements:
            # Find start of horizontal word
            cc = c
            while cc > 0 and temp_grid[r][cc - 1]:
                cc -= 1
            if (r, cc, 'H') not in checked_h:
                word = ''
                positions = []
                tc = cc
                while tc < BOARD_SIZE and temp_grid[r][tc]:
                    word += temp_grid[r][tc]
                    positions.append((r, tc))
                    tc += 1
                if len(word) > 1:
                    words.append((word, positions))
                checked_h.add((r, cc, 'H'))

        # Check vertical words
        checked_v = set()
        for r, c, _ in placements:
            rr = r
            while rr > 0 and temp_grid[rr - 1][c]:
                rr -= 1
            if (rr, c, 'V') not in checked_v:
                word = ''
                positions = []
                tr = rr
                while tr < BOARD_SIZE and temp_grid[tr][c]:
                    word += temp_grid[tr][c]
                    positions.append((tr, c))
                    tr += 1
                if len(word) > 1:
                    words.append((word, positions))
                checked_v.add((rr, c, 'V'))

        return words

    def validate_placement(self, placements):
        """Returns (valid: bool, error_msg: str, words: list)"""
        if not placements:
            return False, "No tiles placed", []

        rows = [r for r, c, _ in placements]
        cols = [c for r, c, _ in placements]

        # Must be in same row or column
        if len(set(rows)) > 1 and len(set(cols)) > 1:
            return False, "Tiles must be in a straight line", []

        # Check no overlap
        for r, c, _ in placements:
            if not self.is_empty(r, c):
                return False, "Square already occupied", []

        # Check connectivity
        if not self.is_connected(placements):
            if self.is_first_move:
                return False, "First word must cover center square", []
            return False, "Tiles must connect to existing words", []

        # Check gaps (tiles must be contiguous with existing tiles)
        if len(set(rows)) == 1:
            r = rows[0]
            min_c, max_c = min(cols), max(cols)
            temp_grid = [row[:] for row in self.grid]
            for pr, pc, letter in placements:
                temp_grid[pr][pc] = letter
            for c in range(min_c, max_c + 1):
                if not temp_grid[r][c]:
                    return False, "Tiles must be contiguous", []
        elif len(set(cols)) == 1:
            c = cols[0]
            min_r, max_r = min(rows), max(rows)
            temp_grid = [row[:] for row in self.grid]
            for pr, pc, letter in placements:
                temp_grid[pr][pc] = letter
            for r in range(min_r, max_r + 1):
                if not temp_grid[r][c]:
                    return False, "Tiles must be contiguous", []

        # Get words formed
        words = self.get_words_from_placements(placements)
        if not words:
            return False, "No word formed", []

        # Validate each word
        for word, _ in words:
            if not is_valid_word(word):
                return False, f'"{word}" is not a valid word', []

        return True, "", words

    def calculate_score(self, placements, words):
        """Calculate score for the play"""
        temp_grid = [row[:] for row in self.grid]
        for r, c, letter in placements:
            temp_grid[r][c] = letter

        placement_set = {(r, c) for r, c, _ in placements}
        total = 0

        for word, positions in words:
            word_mult = 1
            word_score = 0
            for r, c in positions:
                letter = temp_grid[r][c]
                letter_val = TILE_VALUES.get(letter, 0)
                premium = PREMIUM_SQUARES.get((r, c))
                # Premium squares only count for NEW tiles
                if (r, c) in placement_set:
                    if premium == 'TL':
                        letter_val *= 3
                    elif premium == 'DL':
                        letter_val *= 2
                    elif premium == 'TW':
                        word_mult *= 3
                    elif premium == 'DW':
                        word_mult *= 2
                word_score += letter_val
            total += word_score * word_mult

        # Bingo bonus: 50 points for using all 7 tiles
        if len(placements) == 7:
            total += 50

        return total

    def commit_placements(self, placements):
        for r, c, letter in placements:
            self.grid[r][c] = letter
        self.is_first_move = False


# ── Player ────────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, name, is_ai=False, ai_difficulty='medium'):
        self.name = name
        self.is_ai = is_ai
        self.ai_difficulty = ai_difficulty
        self.rack = []
        self.score = 0
        self.passes = 0

    def fill_rack(self, bag):
        needed = 7 - len(self.rack)
        drawn = bag.draw(needed)
        self.rack.extend(drawn)

    def remove_from_rack(self, letters):
        rack_copy = self.rack[:]
        for l in letters:
            if l in rack_copy:
                rack_copy.remove(l)
            else:
                return False
        self.rack = rack_copy
        return True

    def has_tiles(self):
        return len(self.rack) > 0


# ── AI Player Logic ───────────────────────────────────────────────────────────
class AIPlayer:
    """Simple AI that tries to find valid words to play"""

    def __init__(self, player):
        self.player = player

    def find_move(self, board):
        """Find a valid move. Returns placements list or None to pass."""
        from data.words import get_word_list
        rack = self.player.rack[:]
        words = get_word_list()

        best_move = None
        best_score = -1

        # Try placing words on the board
        attempts = 0
        for word in random.sample(list(words), min(800, len(words))):
            if attempts > 2000:
                break
            attempts += 1
            word_upper = word.upper()
            # Check if we can form this word with our rack
            if not self._can_form(word_upper, rack):
                continue
            # Try different positions
            move = self._try_place_word(board, word_upper, rack)
            if move:
                valid, msg, found_words = board.validate_placement(move)
                if valid:
                    score = board.calculate_score(move, found_words)
                    if score > best_score:
                        best_score = score
                        best_move = move

        return best_move

    def _can_form(self, word, rack):
        rack_copy = rack[:]
        for letter in word:
            if letter in rack_copy:
                rack_copy.remove(letter)
            elif '_' in rack_copy:  # blank tile
                rack_copy.remove('_')
            else:
                return False
        return True

    def _try_place_word(self, board, word, rack):
        """Try to place a word on the board, returns placements or None.
        Tries both horizontal and vertical orientations through every
        existing tile whose letter appears in the word."""
        if board.is_first_move:
            # Try horizontal through center
            for start_c in range(max(0, 7 - len(word) + 1), min(8, BOARD_SIZE - len(word) + 1)):
                if start_c + len(word) <= BOARD_SIZE:
                    covers_center = any(start_c + i == 7 for i in range(len(word)))
                    if covers_center:
                        return [(7, start_c + i, letter) for i, letter in enumerate(word)]
            # Try vertical through center
            for start_r in range(max(0, 7 - len(word) + 1), min(8, BOARD_SIZE - len(word) + 1)):
                if start_r + len(word) <= BOARD_SIZE:
                    covers_center = any(start_r + i == 7 for i in range(len(word)))
                    if covers_center:
                        return [(start_r + i, 7, letter) for i, letter in enumerate(word)]
            return None

        # Try to hook onto every existing tile, in both orientations
        candidates = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                existing = board.grid[r][c]
                if not existing:
                    continue
                for i, letter in enumerate(word):
                    if letter != existing:
                        continue
                    # ── Horizontal placement ──────────────────────────────
                    start_c = c - i
                    if 0 <= start_c and start_c + len(word) <= BOARD_SIZE:
                        placements = []
                        ok = True
                        for j, wl in enumerate(word):
                            cell = board.grid[r][start_c + j]
                            if cell is None:
                                placements.append((r, start_c + j, wl))
                            elif cell != wl:
                                ok = False
                                break
                        if ok and placements:
                            candidates.append(placements)

                    # ── Vertical placement ────────────────────────────────
                    start_r = r - i
                    if 0 <= start_r and start_r + len(word) <= BOARD_SIZE:
                        placements = []
                        ok = True
                        for j, wl in enumerate(word):
                            cell = board.grid[start_r + j][c]
                            if cell is None:
                                placements.append((start_r + j, c, wl))
                            elif cell != wl:
                                ok = False
                                break
                        if ok and placements:
                            candidates.append(placements)

        return candidates[0] if candidates else None


# ── Game State Machine ────────────────────────────────────────────────────────
class ScrbleGame:
    def __init__(self, player_configs):
        """
        player_configs: list of dicts with keys: name, is_ai, ai_difficulty
        """
        self.board = Board()
        self.bag = TileBag()
        self.players = []
        for cfg in player_configs:
            p = Player(cfg['name'], cfg.get('is_ai', False), cfg.get('ai_difficulty', 'medium'))
            self.players.append(p)

        self.current_idx = 0
        self.consecutive_passes = 0
        self.game_over = False
        self.winner = None
        self.pending_placements = []  # tiles placed this turn, not yet committed

        # Deal tiles
        for p in self.players:
            p.fill_rack(self.bag)

    @property
    def current_player(self):
        return self.players[self.current_idx]

    def place_tile(self, row, col, letter):
        """Place a tile from current player's rack to board (pending)"""
        if letter not in self.current_player.rack:
            return False, "Tile not in rack"
        if not self.board.is_empty(row, col):
            # Check if it's a pending placement we placed this turn
            if any(r == row and c == col for r, c, _ in self.pending_placements):
                return False, "Square already used this turn"
            return False, "Square occupied"
        # Remove from rack
        rack = self.current_player.rack
        rack.remove(letter)
        self.pending_placements.append((row, col, letter))
        return True, ""

    def recall_tile(self, row, col):
        """Return a pending tile back to rack"""
        for i, (r, c, letter) in enumerate(self.pending_placements):
            if r == row and c == col:
                self.pending_placements.pop(i)
                self.current_player.rack.append(letter)
                return True, letter
        return False, ""

    def recall_all(self):
        """Return all pending tiles to rack"""
        for r, c, letter in self.pending_placements:
            self.current_player.rack.append(letter)
        self.pending_placements = []

    def submit_word(self):
        """Try to commit the current pending placements"""
        if not self.pending_placements:
            return False, "No tiles placed"

        valid, msg, words = self.board.validate_placement(self.pending_placements)
        if not valid:
            return False, msg

        score = self.board.calculate_score(self.pending_placements, words)
        self.board.commit_placements(self.pending_placements)
        self.current_player.score += score
        self.current_player.passes = 0

        formed_words = [w for w, _ in words]
        self.pending_placements = []

        # Refill rack
        self.current_player.fill_rack(self.bag)

        # Check if player used all tiles and bag is empty
        if not self.current_player.has_tiles() and self.bag.remaining() == 0:
            self._end_game()
            return True, f"+{score} points! Words: {', '.join(formed_words)}"

        self.consecutive_passes = 0
        self._next_turn()
        return True, f"+{score} points! Words: {', '.join(formed_words)}"

    def pass_turn(self):
        """Pass the current turn"""
        self.recall_all()
        self.current_player.passes += 1
        self.consecutive_passes += 1
        if self.consecutive_passes >= max(6, len(self.players) * 3):
            self._end_game()
            return "Game ended - too many passes"
        self._next_turn()
        return "Turn passed"

    def swap_tiles(self, letters_to_swap):
        """Swap tiles with the bag"""
        if self.bag.remaining() < len(letters_to_swap):
            return False, "Not enough tiles in bag to swap"
        self.recall_all()
        for l in letters_to_swap:
            if l not in self.current_player.rack:
                return False, f"Tile {l} not in rack"
        for l in letters_to_swap:
            self.current_player.rack.remove(l)
        new_tiles = self.bag.swap(letters_to_swap)
        if new_tiles:
            self.current_player.rack.extend(new_tiles)
        self.consecutive_passes += 1
        self._next_turn()
        return True, f"Swapped {len(letters_to_swap)} tiles"

    def do_ai_turn(self):
        """Execute AI player's turn, returns result message"""
        ai = AIPlayer(self.current_player)
        move = ai.find_move(self.board)
        if move:
            self.pending_placements = move
            # Remove from rack
            for r, c, letter in move:
                if letter in self.current_player.rack:
                    self.current_player.rack.remove(letter)
            success, msg = self.submit_word()
            return msg
        else:
            return self.pass_turn()

    def _next_turn(self):
        self.current_idx = (self.current_idx + 1) % len(self.players)

    def _end_game(self):
        self.game_over = True
        # Subtract remaining rack values
        for p in self.players:
            rack_val = sum(TILE_VALUES.get(t, 0) for t in p.rack)
            p.score -= rack_val
        # Winner = highest score
        self.winner = max(self.players, key=lambda p: p.score)

    def get_scores(self):
        return [(p.name, p.score, p.is_ai) for p in self.players]

    def get_board_state(self):
        return self.board.grid

    def tiles_remaining(self):
        return self.bag.remaining()
