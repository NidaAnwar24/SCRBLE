"""
Scrble - Home & Player Setup Screen
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window


# ── Color Palette ─────────────────────────────────────────────────────────────
BG_DARK      = (0.08, 0.09, 0.13, 1)
BG_CARD      = (0.13, 0.15, 0.20, 1)
ACCENT_GOLD  = (0.95, 0.75, 0.25, 1)
ACCENT_TEAL  = (0.20, 0.80, 0.65, 1)
TEXT_WHITE   = (0.95, 0.95, 0.95, 1)
TEXT_MUTED   = (0.55, 0.58, 0.65, 1)
BTN_GREEN    = (0.20, 0.75, 0.45, 1)
BTN_RED      = (0.85, 0.30, 0.30, 1)
AI_PURPLE    = (0.55, 0.35, 0.85, 1)


def rgba(color):
    return color


class RoundedButton(Button):
    def __init__(self, bg_color=ACCENT_GOLD, text_color=BG_DARK, radius=12, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.text_color = text_color
        self.radius = radius
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        self.bold = True
        self.font_size = sp(15)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(self.radius)])

    def on_press(self):
        anim = Animation(opacity=0.7, duration=0.05) + Animation(opacity=1.0, duration=0.05)
        anim.start(self)


class PlayerRow(BoxLayout):
    """A row for one player's setup: name input, AI toggle"""

    def __init__(self, player_num, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self.spacing = dp(8)
        self.padding = [dp(4), dp(4)]
        self.player_num = player_num
        self.is_ai = False

        # Background
        with self.canvas.before:
            Color(*BG_CARD)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Player number badge
        num_lbl = Label(
            text=f'P{player_num}',
            size_hint=(None, 1),
            width=dp(36),
            bold=True,
            color=ACCENT_GOLD,
            font_size=sp(14),
        )
        self.add_widget(num_lbl)

        # Name input
        self.name_input = TextInput(
            hint_text=f'Player {player_num}',
            text=f'Player {player_num}',
            size_hint=(1, None),
            height=dp(40),
            multiline=False,
            background_color=(0.18, 0.21, 0.28, 1),
            foreground_color=TEXT_WHITE,
            hint_text_color=TEXT_MUTED,
            cursor_color=ACCENT_GOLD,
            font_size=sp(14),
            padding=[dp(10), dp(8)],
        )
        self.add_widget(self.name_input)

        # AI toggle
        self.ai_btn = ToggleButton(
            text='Human',
            size_hint=(None, None),
            size=(dp(72), dp(40)),
            group=None,
            bold=True,
            font_size=sp(11),
            background_color=(0, 0, 0, 0),
            color=TEXT_MUTED,
        )
        self.ai_btn.bind(on_press=self._toggle_ai)
        self._draw_ai_btn()
        self.add_widget(self.ai_btn)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _toggle_ai(self, btn):
        self.is_ai = not self.is_ai
        if self.is_ai:
            self.ai_btn.text = '🤖 AI'
            self.ai_btn.color = AI_PURPLE
            self.name_input.text = f'AI Bot {self.player_num}'
            self.name_input.disabled = True
        else:
            self.ai_btn.text = 'Human'
            self.ai_btn.color = TEXT_MUTED
            self.name_input.text = f'Player {self.player_num}'
            self.name_input.disabled = False

    def _draw_ai_btn(self):
        self.ai_btn.canvas.before.clear()
        with self.ai_btn.canvas.before:
            Color(*(AI_PURPLE if self.is_ai else (0.25, 0.27, 0.35, 1)))
            RoundedRectangle(pos=self.ai_btn.pos, size=self.ai_btn.size, radius=[dp(8)])
        self.ai_btn.bind(pos=self._redraw_ai, size=self._redraw_ai)

    def _redraw_ai(self, *args):
        self._draw_ai_btn()

    def get_config(self):
        return {
            'name': self.name_input.text.strip() or f'Player {self.player_num}',
            'is_ai': self.is_ai,
            'ai_difficulty': 'medium',
        }


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_rows = []
        self._build_ui()

    def _build_ui(self):
        # Root with dark background
        root = BoxLayout(orientation='vertical', padding=0, spacing=0)

        with root.canvas.before:
            Color(*BG_DARK)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self.bg, 'pos', root.pos),
                  size=lambda *a: setattr(self.bg, 'size', root.size))

        # ── Header ────────────────────────────────────────────────────────────
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(160),
            padding=[dp(20), dp(24), dp(20), dp(12)],
        )

        title = Label(
            text='[b]SCRBLE[/b]',
            markup=True,
            font_size=sp(48),
            color=ACCENT_GOLD,
            size_hint_y=None,
            height=dp(64),
        )
        subtitle = Label(
            text='The Word Strategy Game',
            font_size=sp(14),
            color=TEXT_MUTED,
            size_hint_y=None,
            height=dp(24),
        )
        tiles_deco = Label(
            text='[color=2ec8a6]S[/color][color=f2c133]C[/color]'
                 '[color=ffffff]R[/color][color=2ec8a6]B[/color]'
                 '[color=f2c133]L[/color][color=ffffff]E[/color]',
            markup=True,
            font_size=sp(20),
            size_hint_y=None,
            height=dp(32),
        )

        header.add_widget(title)
        header.add_widget(subtitle)
        header.add_widget(tiles_deco)
        root.add_widget(header)

        # ── Player Count Selector ─────────────────────────────────────────────
        count_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(90),
            padding=[dp(20), dp(8)],
            spacing=dp(8),
        )
        count_lbl = Label(
            text='Number of Players',
            font_size=sp(13),
            color=TEXT_MUTED,
            size_hint_y=None,
            height=dp(20),
            halign='left',
        )
        count_lbl.bind(size=count_lbl.setter('text_size'))

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(46),
            spacing=dp(8),
        )
        self.count_btns = []
        for i in range(2, 7):
            btn = ToggleButton(
                text=str(i),
                group='player_count',
                size_hint=(1, 1),
                bold=True,
                font_size=sp(16),
                background_color=(0, 0, 0, 0),
                color=TEXT_WHITE,
            )
            btn.player_count = i
            btn.bind(on_press=self._on_count_select)
            self.count_btns.append(btn)
            btn_row.add_widget(btn)
            self._style_count_btn(btn, selected=(i == 2))

        count_section.add_widget(count_lbl)
        count_section.add_widget(btn_row)
        root.add_widget(count_section)

        # ── Player Setup Area ─────────────────────────────────────────────────
        setup_lbl = Label(
            text='Player Setup',
            font_size=sp(13),
            color=TEXT_MUTED,
            size_hint_y=None,
            height=dp(24),
            halign='left',
            padding_x=dp(20),
        )
        setup_lbl.bind(size=setup_lbl.setter('text_size'))
        root.add_widget(setup_lbl)

        self.players_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
        )
        self.players_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8),
            padding=[dp(16), dp(4), dp(16), dp(8)],
        )
        self.players_container.bind(
            minimum_height=self.players_container.setter('height')
        )
        self.players_scroll.add_widget(self.players_container)
        root.add_widget(self.players_scroll)

        # ── Start Button ──────────────────────────────────────────────────────
        btn_area = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=[dp(20), dp(12)],
        )
        start_btn = RoundedButton(
            text='▶  START GAME',
            bg_color=BTN_GREEN,
            text_color=(1, 1, 1, 1),
            radius=14,
            font_size=sp(17),
        )
        start_btn.bind(on_press=self._start_game)
        btn_area.add_widget(start_btn)
        root.add_widget(btn_area)

        self.add_widget(root)

        # Initialize with 2 players
        self._set_player_count(2)
        # Select first button
        self.count_btns[0].state = 'down'

    def _style_count_btn(self, btn, selected=False):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if selected:
                Color(*ACCENT_GOLD)
                btn.color = BG_DARK
            else:
                Color(0.20, 0.22, 0.30, 1)
                btn.color = TEXT_WHITE
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(10)])
        btn.bind(pos=lambda *a: self._restyle_btn(btn),
                 size=lambda *a: self._restyle_btn(btn))

    def _restyle_btn(self, btn):
        selected = btn.state == 'down'
        btn.canvas.before.clear()
        with btn.canvas.before:
            if selected:
                Color(*ACCENT_GOLD)
                btn.color = BG_DARK
            else:
                Color(0.20, 0.22, 0.30, 1)
                btn.color = TEXT_WHITE
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(10)])

    def _on_count_select(self, btn):
        for b in self.count_btns:
            self._restyle_btn(b)
        self._set_player_count(btn.player_count)

    def _set_player_count(self, count):
        self.players_container.clear_widgets()
        self.player_rows = []
        for i in range(1, count + 1):
            row = PlayerRow(player_num=i)
            self.player_rows.append(row)
            self.players_container.add_widget(row)

    def _start_game(self, *args):
        configs = [row.get_config() for row in self.player_rows]
        # Validate at least 2 players
        if len(configs) < 2:
            self._show_error("Need at least 2 players!")
            return
        # Pass configs to game screen
        game_screen = self.manager.get_screen('game')
        game_screen.start_new_game(configs)
        self.manager.current = 'game'

    def _show_error(self, msg):
        popup = Popup(
            title='Setup Error',
            content=Label(text=msg, color=BTN_RED),
            size_hint=(0.7, 0.3),
        )
        popup.open()
