"""
Scrble - Main Game Screen  (crash-fixed rewrite)
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation

from game.engine import ScrbleGame, PREMIUM_SQUARES, TILE_VALUES, BOARD_SIZE

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK     = (0.08, 0.09, 0.13, 1)
BG_CARD     = (0.13, 0.15, 0.20, 1)
ACCENT_GOLD = (0.95, 0.75, 0.25, 1)
ACCENT_TEAL = (0.20, 0.80, 0.65, 1)
TEXT_WHITE  = (0.95, 0.95, 0.95, 1)
TEXT_MUTED  = (0.55, 0.58, 0.65, 1)
BTN_GREEN   = (0.20, 0.75, 0.45, 1)
BTN_RED     = (0.85, 0.30, 0.30, 1)
BTN_BLUE    = (0.25, 0.55, 0.90, 1)
AI_PURPLE   = (0.55, 0.35, 0.85, 1)

SQUARE_COLORS = {
    None: (0.16, 0.19, 0.25, 1),
    'TW': (0.80, 0.22, 0.22, 1),
    'DW': (0.85, 0.42, 0.22, 1),
    'TL': (0.22, 0.50, 0.85, 1),
    'DL': (0.35, 0.68, 0.90, 1),
}
PLACED_COLOR  = (0.95, 0.82, 0.40, 1)
PENDING_COLOR = (0.95, 0.65, 0.20, 1)
CENTER_COLOR  = (0.85, 0.25, 0.55, 1)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _bg(widget, color):
    """Attach a self-updating background rectangle to any widget."""
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda w, v: setattr(rect, 'pos', v),
                size=lambda w, v: setattr(rect, 'size', v))


def _rounded_bg(widget, color, radius=10):
    """Attach a self-updating rounded-rect background."""
    with widget.canvas.before:
        Color(*color)
        rect = RoundedRectangle(pos=widget.pos, size=widget.size,
                                radius=[dp(radius)])
    widget.bind(pos=lambda w, v: setattr(rect, 'pos', v),
                size=lambda w, v: setattr(rect, 'size', v))


class FlatButton(Button):
    """A button with a solid rounded background and no Kivy chrome."""
    def __init__(self, bg=ACCENT_GOLD, fg=BG_DARK, radius=10, **kw):
        super().__init__(**kw)
        self.background_color = (0, 0, 0, 0)
        self.color = fg
        self.bold = True
        self.font_size = sp(13)
        with self.canvas.before:
            self._c = Color(*bg)
            self._r = RoundedRectangle(pos=self.pos, size=self.size,
                                       radius=[dp(radius)])
        self.bind(pos=lambda w, v: setattr(self._r, 'pos', v),
                  size=lambda w, v: setattr(self._r, 'size', v))

    def recolor(self, bg=None, fg=None):
        if bg:
            self._c.rgba = bg
        if fg:
            self.color = fg

    def on_press(self):
        anim = Animation(opacity=0.6, d=0.07) + Animation(opacity=1.0, d=0.07)
        anim.start(self)


# ── Board Cell ────────────────────────────────────────────────────────────────
class BoardCell(Button):
    def __init__(self, row, col, game_screen, cell_px, **kw):
        super().__init__(size_hint=(None, None),
                         size=(cell_px, cell_px), **kw)
        self.row, self.col = row, col
        self.game_screen = game_screen
        self.letter = None
        self.is_pending = False
        self.background_color = (0, 0, 0, 0)
        self.font_size = sp(10)
        self.bold = True
        self.markup = True

        ptype = PREMIUM_SQUARES.get((row, col))
        if (row, col) == (7, 7):
            base = CENTER_COLOR
        else:
            base = SQUARE_COLORS.get(ptype, SQUARE_COLORS[None])

        with self.canvas.before:
            self._fill_c = Color(*base)
            self._fill_r = RoundedRectangle(
                pos=(self.x + dp(1), self.y + dp(1)),
                size=(self.width - dp(2), self.height - dp(2)),
                radius=[dp(2)])
        self.bind(pos=self._redraw, size=self._redraw)
        self._set_default_label()

    def _redraw(self, *_):
        self._fill_r.pos  = (self.x + dp(1), self.y + dp(1))
        self._fill_r.size = (self.width - dp(2), self.height - dp(2))

    def _set_default_label(self):
        ptype = PREMIUM_SQUARES.get((self.row, self.col))
        if (self.row, self.col) == (7, 7):
            self.text = '[color=ffffff]★[/color]'
        elif ptype == 'TW':
            self.text = '[size=7][color=ffcccc]TW[/color][/size]'
        elif ptype == 'DW':
            self.text = '[size=7][color=ffd9b3]DW[/color][/size]'
        elif ptype == 'TL':
            self.text = '[size=7][color=cce0ff]TL[/color][/size]'
        elif ptype == 'DL':
            self.text = '[size=7][color=d9f0ff]DL[/color][/size]'
        else:
            self.text = ''

    def set_letter(self, letter, pending=False):
        self.letter = letter
        self.is_pending = pending
        if letter:
            if pending:
                self._fill_c.rgba = PENDING_COLOR
            else:
                self._fill_c.rgba = PLACED_COLOR
            val = TILE_VALUES.get(letter, 0)
            self.text = (f'[color=1a1a1a][b]{letter}[/b][/color]'
                         f'\n[size=7][color=333333]{val}[/color][/size]')
        else:
            ptype = PREMIUM_SQUARES.get((self.row, self.col))
            if (self.row, self.col) == (7, 7):
                self._fill_c.rgba = CENTER_COLOR
            else:
                self._fill_c.rgba = SQUARE_COLORS.get(ptype, SQUARE_COLORS[None])
            self._set_default_label()

    def on_press(self):
        self.game_screen.on_cell_press(self.row, self.col)


# ── Rack Tile ─────────────────────────────────────────────────────────────────
class RackTile(Button):
    def __init__(self, letter, game_screen, **kw):
        super().__init__(size_hint=(None, 1), width=dp(44), **kw)
        self.letter = letter
        self.game_screen = game_screen
        self.selected = False
        self.background_color = (0, 0, 0, 0)
        self.bold = True
        self.font_size = sp(17)
        self.markup = True
        val = TILE_VALUES.get(letter, 0)
        self.text = (f'[color=1a1a1a][b]{letter}[/b][/color]'
                     f'\n[size=9][color=333333]{val}[/color][/size]')

        with self.canvas.before:
            self._c = Color(*ACCENT_GOLD)
            self._r = RoundedRectangle(pos=(self.x+dp(2), self.y+dp(2)),
                                       size=(self.width-dp(4), self.height-dp(4)),
                                       radius=[dp(7)])
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self._r.pos  = (self.x+dp(2), self.y+dp(2))
        self._r.size = (self.width-dp(4), self.height-dp(4))

    def set_selected(self, val):
        self.selected = val
        self._c.rgba = (1.0, 0.95, 0.3, 1) if val else ACCENT_GOLD

    def on_press(self):
        self.game_screen.on_rack_tile_press(self)


# ── Score Panel ───────────────────────────────────────────────────────────────
class ScorePanel(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='horizontal',
                         spacing=dp(4), padding=[dp(6), dp(4)], **kw)
        self._labels = {}   # name -> (name_lbl, score_lbl)

    def setup(self, players):
        self.clear_widgets()
        self._labels = {}
        for p in players:
            col = BoxLayout(orientation='vertical', spacing=dp(1))
            icon = '🤖' if p.is_ai else '👤'
            nl = Label(text=f'{icon} {p.name[:7]}',
                       font_size=sp(9), color=TEXT_MUTED, bold=True,
                       size_hint_y=None, height=dp(15),
                       halign='center', valign='middle')
            nl.bind(size=nl.setter('text_size'))
            sl = Label(text='0', font_size=sp(16), color=ACCENT_GOLD, bold=True,
                       size_hint_y=None, height=dp(24),
                       halign='center', valign='middle')
            sl.bind(size=sl.setter('text_size'))
            col.add_widget(nl)
            col.add_widget(sl)
            self._labels[p.name] = (nl, sl)
            self.add_widget(col)

    def refresh(self, scores, current_name):
        for name, score, is_ai in scores:
            if name not in self._labels:
                continue
            nl, sl = self._labels[name]
            sl.text = str(score)
            if name == current_name:
                nl.color = ACCENT_TEAL
                sl.color = ACCENT_TEAL
            else:
                nl.color = TEXT_MUTED
                sl.color = ACCENT_GOLD


# ── Game Screen ───────────────────────────────────────────────────────────────
class GameScreen(Screen):

    CELL_PX = dp(32)   # fixed cell size – safe, no Window reference needed

    def __init__(self, **kw):
        super().__init__(**kw)
        self.game = None
        self.cells = {}
        self.rack_tiles = []
        self.selected_rack_tile = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        root = BoxLayout(orientation='vertical')
        _bg(root, BG_DARK)

        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(42),
                            padding=[dp(12), dp(6)], spacing=dp(8))
        _bg(top_bar, BG_CARD)

        self.turn_lbl = Label(text='', font_size=sp(13), bold=True,
                              color=ACCENT_TEAL, halign='left')
        self.turn_lbl.bind(size=self.turn_lbl.setter('text_size'))
        self.bag_lbl  = Label(text='🎒 100', font_size=sp(12),
                              color=TEXT_MUTED, size_hint_x=None,
                              width=dp(62), halign='right')
        self.bag_lbl.bind(size=self.bag_lbl.setter('text_size'))
        top_bar.add_widget(self.turn_lbl)
        top_bar.add_widget(self.bag_lbl)
        root.add_widget(top_bar)

        # Score panel
        self.score_panel = ScorePanel(size_hint_y=None, height=dp(46))
        _bg(self.score_panel, (0.10, 0.12, 0.17, 1))
        root.add_widget(self.score_panel)

        # Board (scrollable)
        scroll = ScrollView(size_hint=(1, 1),
                            do_scroll_x=True, do_scroll_y=True)
        board_px = self.CELL_PX * BOARD_SIZE
        self.board_grid = GridLayout(
            cols=BOARD_SIZE,
            size_hint=(None, None),
            width=board_px, height=board_px,
            row_default_height=self.CELL_PX,
            row_force_default=True,
            col_default_width=self.CELL_PX,
            col_force_default=True,
            spacing=0, padding=0,
        )
        scroll.add_widget(self.board_grid)
        root.add_widget(scroll)

        # Message bar
        self.msg_lbl = Label(text='Select a tile then tap the board',
                             font_size=sp(11), color=ACCENT_TEAL,
                             size_hint_y=None, height=dp(26),
                             halign='center')
        self.msg_lbl.bind(size=self.msg_lbl.setter('text_size'))
        root.add_widget(self.msg_lbl)

        # Rack
        rack_wrap = BoxLayout(size_hint_y=None, height=dp(72))
        _bg(rack_wrap, BG_CARD)
        self.rack_box = BoxLayout(orientation='horizontal',
                                  spacing=dp(6), padding=[dp(10), dp(8)])
        rack_wrap.add_widget(self.rack_box)
        root.add_widget(rack_wrap)

        # Action bar
        act = BoxLayout(size_hint_y=None, height=dp(52),
                        spacing=dp(6), padding=[dp(8), dp(6)])
        _bg(act, BG_DARK)

        self.btn_play   = FlatButton(text='✓ PLAY',   bg=BTN_GREEN,
                                     fg=(1,1,1,1), size_hint=(1.5,1))
        self.btn_recall = FlatButton(text='↩ RECALL', bg=(0.22,0.25,0.33,1),
                                     fg=TEXT_WHITE, size_hint=(1,1))
        self.btn_pass   = FlatButton(text='PASS',     bg=(0.22,0.25,0.33,1),
                                     fg=TEXT_WHITE, size_hint=(1,1))
        self.btn_swap   = FlatButton(text='⇄ SWAP',   bg=BTN_BLUE,
                                     fg=(1,1,1,1), size_hint=(1,1))

        self.btn_play.bind(on_press=self._submit)
        self.btn_recall.bind(on_press=lambda *_: (self.game.recall_all(),
                                                   self._refresh()) or None)
        self.btn_pass.bind(on_press=self._pass)
        self.btn_swap.bind(on_press=self._swap)

        for b in (self.btn_play, self.btn_recall, self.btn_pass, self.btn_swap):
            act.add_widget(b)
        root.add_widget(act)

        self.add_widget(root)

    # ── Game start ────────────────────────────────────────────────────────────
    def start_new_game(self, configs):
        self.game = ScrbleGame(configs)
        self.selected_rack_tile = None

        # Build board cells
        self.board_grid.clear_widgets()
        self.cells = {}
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = BoardCell(r, c, self, self.CELL_PX)
                self.cells[(r, c)] = cell
                self.board_grid.add_widget(cell)

        self.score_panel.setup(self.game.players)
        self._refresh()

        if self.game.current_player.is_ai:
            Clock.schedule_once(self._ai_turn, 1.2)

    # ── Refresh all UI from game state ────────────────────────────────────────
    def _refresh(self):
        if not self.game:
            return
        p = self.game.current_player
        icon = '🤖' if p.is_ai else '👤'
        self.turn_lbl.text = f"{icon}  {p.name}'s Turn"
        self.bag_lbl.text  = f'🎒 {self.game.tiles_remaining()}'
        self.score_panel.refresh(self.game.get_scores(), p.name)

        # Board
        grid    = self.game.get_board_state()
        pending = {(r, c): l for r, c, l in self.game.pending_placements}
        for (r, c), cell in self.cells.items():
            if (r, c) in pending:
                cell.set_letter(pending[(r, c)], pending=True)
            elif grid[r][c]:
                cell.set_letter(grid[r][c], pending=False)
            else:
                cell.set_letter(None)

        # Rack
        self.rack_box.clear_widgets()
        self.rack_tiles = []
        self.selected_rack_tile = None
        for letter in p.rack:
            t = RackTile(letter, self)
            self.rack_tiles.append(t)
            self.rack_box.add_widget(t)
        self.rack_box.add_widget(Widget())   # spacer

        # Disable during AI turn
        ai = p.is_ai
        for b in (self.btn_play, self.btn_recall, self.btn_pass, self.btn_swap):
            b.disabled = ai

    def _msg(self, text, color=None):
        self.msg_lbl.text  = text
        self.msg_lbl.color = color or ACCENT_TEAL

    # ── Input handling ────────────────────────────────────────────────────────
    def on_rack_tile_press(self, tile):
        if self.game and self.game.current_player.is_ai:
            return
        if self.selected_rack_tile is tile:
            tile.set_selected(False)
            self.selected_rack_tile = None
            self._msg('Tile deselected')
        else:
            if self.selected_rack_tile:
                self.selected_rack_tile.set_selected(False)
            tile.set_selected(True)
            self.selected_rack_tile = tile
            self._msg(f'[{tile.letter}] selected — tap a board square')

    def on_cell_press(self, row, col):
        if not self.game or self.game.current_player.is_ai:
            return
        pending = {(r, c) for r, c, _ in self.game.pending_placements}
        grid    = self.game.get_board_state()

        if (row, col) in pending:
            ok, letter = self.game.recall_tile(row, col)
            if ok:
                self._msg(f'[{letter}] recalled')
            self.selected_rack_tile = None
            self._refresh()
            return

        if not self.selected_rack_tile:
            self._msg('Select a tile from your rack first')
            return

        if grid[row][col]:
            self._msg('That square is already occupied')
            return

        ok, err = self.game.place_tile(row, col, self.selected_rack_tile.letter)
        if ok:
            self.selected_rack_tile = None
            self._msg('Tile placed — tap it again to recall')
        else:
            self._msg(err, BTN_RED)
        self._refresh()

    # ── Action handlers ───────────────────────────────────────────────────────
    def _submit(self, *_):
        ok, msg = self.game.submit_word()
        if ok:
            self._msg(msg, ACCENT_TEAL)
            self._refresh()
            self._check_over()
            if not self.game.game_over and self.game.current_player.is_ai:
                Clock.schedule_once(self._ai_turn, 1.0)
        else:
            self._msg(f'❌ {msg}', BTN_RED)
            self._refresh()

    def _pass(self, *_):
        msg = self.game.pass_turn()
        self._msg(msg)
        self._refresh()
        self._check_over()
        if not self.game.game_over and self.game.current_player.is_ai:
            Clock.schedule_once(self._ai_turn, 1.0)

    def _swap(self, *_):
        if self.game.tiles_remaining() < 1:
            self._msg('Not enough tiles in bag', BTN_RED)
            return

        content = BoxLayout(orientation='vertical',
                            spacing=dp(10), padding=dp(12))
        _bg(content, BG_DARK)

        content.add_widget(Label(text='Tap tiles to swap, then confirm:',
                                 font_size=sp(12), color=TEXT_MUTED,
                                 size_hint_y=None, height=dp(24)))

        tile_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        to_swap  = []

        def toggle(btn, letter):
            if letter in to_swap:
                to_swap.remove(letter)
                btn._c.rgba = ACCENT_GOLD
                btn.color   = (0.1, 0.1, 0.1, 1)
            else:
                to_swap.append(letter)
                btn._c.rgba = BTN_RED
                btn.color   = (1, 1, 1, 1)

        popup = Popup(title='Swap Tiles', content=content,
                      size_hint=(0.85, 0.50),
                      background_color=BG_CARD,
                      separator_color=ACCENT_GOLD)

        for letter in self.game.current_player.rack:
            btn = FlatButton(text=letter, bg=ACCENT_GOLD,
                             fg=(0.1, 0.1, 0.1, 1),
                             size_hint=(None, 1), width=dp(44),
                             font_size=sp(18))
            lt = letter
            btn.bind(on_press=lambda b, l=lt: toggle(b, l))
            tile_row.add_widget(btn)
        content.add_widget(tile_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        cancel = FlatButton(text='Cancel', bg=BG_CARD, fg=TEXT_WHITE)
        confirm = FlatButton(text='Swap', bg=BTN_BLUE, fg=(1, 1, 1, 1))

        def do_swap(*_):
            if not to_swap:
                popup.dismiss()
                return
            ok, msg = self.game.swap_tiles(list(to_swap))
            popup.dismiss()
            self._msg(msg)
            self._refresh()
            if not self.game.game_over and self.game.current_player.is_ai:
                Clock.schedule_once(self._ai_turn, 1.0)

        cancel.bind(on_press=popup.dismiss)
        confirm.bind(on_press=do_swap)
        btn_row.add_widget(cancel)
        btn_row.add_widget(confirm)
        content.add_widget(btn_row)
        popup.open()

    # ── AI turn ───────────────────────────────────────────────────────────────
    def _ai_turn(self, dt):
        if not self.game or self.game.game_over:
            return
        if not self.game.current_player.is_ai:
            return
        self._msg(f'🤖 {self.game.current_player.name} is thinking…', AI_PURPLE)

        def execute(dt2):
            if not self.game or self.game.game_over:
                return
            msg = self.game.do_ai_turn()
            self._msg(f'🤖 {msg}', AI_PURPLE)
            self._refresh()
            self._check_over()
            if not self.game.game_over and self.game.current_player.is_ai:
                Clock.schedule_once(self._ai_turn, 1.5)

        Clock.schedule_once(execute, 0.9)

    # ── Game over ─────────────────────────────────────────────────────────────
    def _check_over(self):
        if self.game and self.game.game_over:
            Clock.schedule_once(self._show_over, 0.4)

    def _show_over(self, dt):
        winner = self.game.winner
        scores = sorted(self.game.get_scores(), key=lambda x: x[1], reverse=True)

        content = BoxLayout(orientation='vertical',
                            spacing=dp(8), padding=[dp(16), dp(14)])
        _bg(content, BG_DARK)

        content.add_widget(Label(text='🏆  Game Over!',
                                 font_size=sp(22), bold=True,
                                 color=ACCENT_GOLD,
                                 size_hint_y=None, height=dp(36)))
        content.add_widget(Label(text=f'Winner: {winner.name}',
                                 font_size=sp(15), bold=True,
                                 color=ACCENT_TEAL,
                                 size_hint_y=None, height=dp(26)))

        for name, score, is_ai in scores:
            icon = '🤖' if is_ai else '👤'
            lbl = Label(text=f'{icon}  {name}:  {score} pts',
                        font_size=sp(13),
                        color=ACCENT_GOLD if name == winner.name else TEXT_WHITE,
                        bold=(name == winner.name),
                        size_hint_y=None, height=dp(22))
            content.add_widget(lbl)

        content.add_widget(Widget())  # spacer

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        home_btn    = FlatButton(text='🏠 Home',       bg=BG_CARD,   fg=TEXT_WHITE)
        again_btn   = FlatButton(text='▶ Play Again',  bg=BTN_GREEN, fg=(1,1,1,1))

        popup = Popup(title='', content=content,
                      size_hint=(0.88, 0.68),
                      background_color=BG_DARK,
                      title_size=0, separator_height=0)

        def on_again(*_):
            popup.dismiss()
            configs = [{'name': p.name, 'is_ai': p.is_ai}
                       for p in self.game.players]
            self.start_new_game(configs)

        def on_home(*_):
            popup.dismiss()
            self.manager.current = 'home'

        home_btn.bind(on_press=on_home)
        again_btn.bind(on_press=on_again)
        btn_row.add_widget(home_btn)
        btn_row.add_widget(again_btn)
        content.add_widget(btn_row)

        popup.open()
