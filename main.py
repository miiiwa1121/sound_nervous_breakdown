import pygame
import numpy as np
import sounddevice as sd
import random
import time
import os


# ======================
# 定数定義
# ======================
class GameConstants:
    """ゲーム全体の定数を管理"""
    # 画面サイズ
    DEFAULT_WIDTH = 600
    DEFAULT_HEIGHT = 600
    
    # カード設定
    CARD_SIZE = 100
    CARD_GAP = 10
    CARD_OFFSET_Y = 60
    
    # 色定義
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (0, 0, 200)
    COLOR_GRAY = (200, 200, 200)
    COLOR_LIGHT_GRAY = (220, 220, 220)
    COLOR_DARK_GREEN = (0, 180, 0)
    COLOR_DARK_RED = (200, 0, 0)
    COLOR_PAUSE_BLUE = (0, 0, 255)
    
    # ボタン設定
    BUTTON_WIDTH = 300
    BUTTON_HEIGHT = 40
    LARGE_BUTTON_HEIGHT = 50
    
    # フォントサイズ
    FONT_SIZE_LARGE = 42
    FONT_SIZE_MEDIUM = 28
    FONT_SIZE_SMALL = 30
    
    # 時間設定
    DEFAULT_TIME_LIMIT = 60
    MIN_TIME_LIMIT = 10
    MAX_TIME_LIMIT = 300
    TIME_ADJUST_STEP = 10
    
    # 音設定
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_TONE_DURATION = 1.0
    DEFAULT_TONE_AMPLITUDE = 0.5
    
    # ゲーム設定
    CARD_COUNT_4X4 = 16
    CARD_COUNT_6X6 = 36


# 音階の定義（周波数）
NOTE_FREQUENCIES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25
}


# ======================
# ユーティリティ関数
# ======================
def play_tone(frequency=440, duration=GameConstants.DEFAULT_TONE_DURATION, 
              sample_rate=GameConstants.DEFAULT_SAMPLE_RATE):
    """指定された周波数の音を再生"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = GameConstants.DEFAULT_TONE_AMPLITUDE * np.sin(2 * np.pi * frequency * t)
    sd.play(wave, samplerate=sample_rate)
    sd.wait()


def get_font(size):
    """日本語対応フォントを取得"""
    available_fonts = pygame.font.get_fonts()
    
    japanese_font_candidates = [
        'msgothic', 'meiryo', 'yumin',
        'hiragino maru gothic pron', 'hiragino kaku gothic pron',
        'noto sans cjk jp', 'noto sans jp', 'noto serif jp',
        'ms gothic', 'yu gothic', 'yu mincho'
    ]
    
    for font_name in japanese_font_candidates:
        for available_font in available_fonts:
            if font_name in available_font.lower():
                return pygame.font.SysFont(font_name, size)
    
    try:
        font_path = os.path.join(os.path.dirname(__file__), "font.ttf")
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
    except:
        pass
    
    return pygame.font.Font(None, size)


# ======================
# ゲームロジック
# ======================
class CardDeck:
    """カードデッキの管理"""
    def __init__(self, num_cards):
        self.num_cards = num_cards
        self.cards = self._shuffle_deck()
        
    def _shuffle_deck(self):
        """カードをシャッフルしてペアを作成"""
        notes = list(NOTE_FREQUENCIES.keys()) * (self.num_cards // 2)
        random.shuffle(notes)
        return notes
    
    def get_card(self, index):
        """指定インデックスのカードを取得"""
        return self.cards[index]
    
    def __len__(self):
        return len(self.cards)


class GameState:
    """ゲーム状態の管理"""
    def __init__(self, card_count, time_limit):
        self.card_count = card_count
        self.time_limit = time_limit
        self.deck = CardDeck(card_count)
        self.card_positions = self._calculate_positions()
        self.card_states = ["hidden"] * card_count
        self.card_values = [None] * card_count
        self.selected_cards = []
        self.matches_found = 0
        self.start_time = time.time()
        self.game_paused = False
        self.pause_start_time = 0
        self.paused_time = 0
        
    def _calculate_positions(self):
        """カードの位置を計算"""
        grid_size = int(self.card_count ** 0.5)
        return [
            (x * (GameConstants.CARD_SIZE + GameConstants.CARD_GAP), 
             y * (GameConstants.CARD_SIZE + GameConstants.CARD_GAP) + GameConstants.CARD_OFFSET_Y)
            for y in range(grid_size) 
            for x in range(grid_size)
        ]
    
    def get_elapsed_time(self):
        """経過時間を計算"""
        if self.game_paused:
            return self.pause_start_time - self.start_time - self.paused_time
        return time.time() - self.start_time - self.paused_time
    
    def get_time_left(self):
        """残り時間を取得"""
        return max(0, self.time_limit - self.get_elapsed_time())
    
    def toggle_pause(self):
        """一時停止の切り替え"""
        if not self.game_paused:
            self.game_paused = True
            self.pause_start_time = time.time()
        else:
            self.game_paused = False
            self.paused_time += time.time() - self.pause_start_time
    
    def flip_card(self, index):
        """カードをめくる"""
        if self.card_states[index] == "hidden":
            self.card_states[index] = "flipped"
            self.selected_cards.append(index)
            play_tone(NOTE_FREQUENCIES[self.deck.get_card(index)])
    
    def check_match(self):
        """選択された2枚のカードがマッチするか確認"""
        if len(self.selected_cards) == 2:
            idx1, idx2 = self.selected_cards
            if self.deck.get_card(idx1) == self.deck.get_card(idx2):
                self.matches_found += 1
                self.card_values[idx1] = self.deck.get_card(idx1)
                self.card_values[idx2] = self.deck.get_card(idx2)
                self.selected_cards = []
                return True
            return False
        return None
    
    def reset_unmatched_cards(self):
        """マッチしなかったカードを裏返す"""
        for idx in self.selected_cards:
            self.card_states[idx] = "hidden"
        self.selected_cards = []
    
    def is_game_complete(self):
        """ゲームが完了したか確認"""
        return self.matches_found == len(self.deck) // 2
    
    def is_time_up(self):
        """時間切れかどうか確認"""
        return self.get_time_left() == 0


# ======================
# UI描画クラス
# ======================
class GameRenderer:
    """ゲーム画面の描画を担当"""
    def __init__(self, screen):
        self.screen = screen
        self.font_large = get_font(GameConstants.FONT_SIZE_LARGE)
        self.font_medium = get_font(GameConstants.FONT_SIZE_MEDIUM)
        self.font_small = get_font(GameConstants.FONT_SIZE_SMALL)
        self.card_font = pygame.font.Font(None, 36)
    
    def draw_menu(self, card_count, time_limit):
        """メニュー画面の描画"""
        self.screen.fill(GameConstants.COLOR_WHITE)
        
        # タイトル
        title_text = self.font_large.render("音階神経衰弱", True, GameConstants.COLOR_BLACK)
        self._center_blit(title_text, 100)
        
        # 4x4ボタン
        button_4x4_color = GameConstants.COLOR_DARK_GREEN if card_count == 16 else GameConstants.COLOR_LIGHT_GRAY
        self._draw_button(button_4x4_color, 200, "4x4 (16カード)")
        
        # 6x6ボタン
        button_6x6_color = GameConstants.COLOR_DARK_GREEN if card_count == 36 else GameConstants.COLOR_LIGHT_GRAY
        self._draw_button(button_6x6_color, 250, "6x6 (36カード)")
        
        # 時間制限表示
        time_label = self.font_medium.render("時間制限:", True, GameConstants.COLOR_BLACK)
        self.screen.blit(time_label, (self._center_x() - 150, 300))
        time_value = self.font_medium.render(f"{time_limit}秒", True, GameConstants.COLOR_BLACK)
        self.screen.blit(time_value, (self._center_x() + 50, 300))
        
        # 時間調整ボタン
        pygame.draw.rect(self.screen, GameConstants.COLOR_DARK_GREEN, 
                        (self._center_x() - 100, 340, 200, GameConstants.BUTTON_HEIGHT))
        time_adjust_text = self.font_medium.render("時間を調整", True, GameConstants.COLOR_WHITE)
        self._center_blit(time_adjust_text, 345)
        
        # 開始ボタン
        pygame.draw.rect(self.screen, GameConstants.COLOR_RED, 
                        (self._center_x() - 100, 400, 200, GameConstants.LARGE_BUTTON_HEIGHT))
        start_text = self.font_medium.render("開始", True, GameConstants.COLOR_WHITE)
        self._center_blit(start_text, 410)
        
        pygame.display.flip()
    
    def draw_time_adjustment(self, time_limit):
        """時間制限調整画面の描画"""
        self.screen.fill(GameConstants.COLOR_WHITE)
        
        # タイトル
        title_text = self.font_large.render("時間制限の調整", True, GameConstants.COLOR_BLACK)
        self._center_blit(title_text, 100)
        
        # 現在の時間制限
        time_text = self.font_medium.render(f"現在の時間制限: {time_limit}秒", True, GameConstants.COLOR_BLACK)
        self._center_blit(time_text, 200)
        
        # 減少ボタン
        pygame.draw.rect(self.screen, GameConstants.COLOR_DARK_RED, 
                        (self._center_x() - 150, 250, 50, 50))
        minus_text = self.font_medium.render("-", True, GameConstants.COLOR_WHITE)
        self.screen.blit(minus_text, (self._center_x() - 135, 260))
        
        # 現在の値
        value_text = self.font_medium.render(f"{time_limit}", True, GameConstants.COLOR_BLACK)
        self._center_blit(value_text, 260)
        
        # 増加ボタン
        pygame.draw.rect(self.screen, GameConstants.COLOR_GREEN, 
                        (self._center_x() + 100, 250, 50, 50))
        plus_text = self.font_medium.render("+", True, GameConstants.COLOR_WHITE)
        self.screen.blit(plus_text, (self._center_x() + 117, 260))
        
        # 確定ボタン
        pygame.draw.rect(self.screen, GameConstants.COLOR_BLUE, 
                        (self._center_x() - 100, 350, 200, GameConstants.LARGE_BUTTON_HEIGHT))
        confirm_text = self.font_medium.render("確定", True, GameConstants.COLOR_WHITE)
        self._center_blit(confirm_text, 365)
        
        pygame.display.flip()
    
    def draw_game(self, game_state):
        """ゲーム画面の描画"""
        self.screen.fill(GameConstants.COLOR_WHITE)
        
        # ステータス表示
        self._draw_game_status(game_state)
        
        # カード描画
        self._draw_cards(game_state)
        
        # 一時停止ボタン
        self._draw_pause_button(game_state.game_paused)
        
        # メニュー戻るボタン（ポーズ中のみ)
        if game_state.game_paused:
            self._draw_menu_button()
        
        pygame.display.flip()
    
    def draw_game_over(self, width, height):
        """ゲーム終了画面の描画"""
        game_over_text = self.font_large.render("ゲーム終了！おめでとう！", True, GameConstants.COLOR_RED)
        self.screen.blit(game_over_text, 
                        (width // 2 - game_over_text.get_width() // 2, 
                         height // 2))
        pygame.display.flip()
    
    def _draw_game_status(self, game_state):
        """スコアと残り時間の表示"""
        score_text = self.font_medium.render(f"スコア: {game_state.matches_found}", 
                                             True, GameConstants.COLOR_BLACK)
        self.screen.blit(score_text, (10, 10))
        
        time_text = self.font_medium.render(f"残り時間: {game_state.get_time_left():.1f}", 
                                           True, GameConstants.COLOR_BLACK)
        self.screen.blit(time_text, (self.screen.get_width() - 250, 10))
    
    def _draw_cards(self, game_state):
        """カードの描画"""
        for i, (x, y) in enumerate(game_state.card_positions):
            if game_state.card_states[i] == "hidden":
                pygame.draw.rect(self.screen, GameConstants.COLOR_GRAY, 
                               (x, y, GameConstants.CARD_SIZE, GameConstants.CARD_SIZE))
            else:
                pygame.draw.rect(self.screen, GameConstants.COLOR_GREEN, 
                               (x, y, GameConstants.CARD_SIZE, GameConstants.CARD_SIZE))
                if game_state.card_values[i] is not None:
                    note_text = self.card_font.render(game_state.card_values[i], 
                                                     True, GameConstants.COLOR_WHITE)
                    self.screen.blit(note_text, 
                                   (x + GameConstants.CARD_SIZE // 4, 
                                    y + GameConstants.CARD_SIZE // 4))
    
    def _draw_pause_button(self, is_paused):
        """一時停止ボタンの描画"""
        color = GameConstants.COLOR_PAUSE_BLUE if is_paused else GameConstants.COLOR_RED
        width = self.screen.get_width()
        pygame.draw.rect(self.screen, color, (width - 100, 50, 80, GameConstants.BUTTON_HEIGHT))
        pause_text = self.font_small.render("停止", True, GameConstants.COLOR_WHITE)
        self.screen.blit(pause_text, (width - 80, 50))
    
    def _draw_menu_button(self):
        """メニュー戻るボタンの描画"""
        width = self.screen.get_width()
        pygame.draw.rect(self.screen, (50, 50, 200), 
                        (width - 200, 60, 150, GameConstants.BUTTON_HEIGHT))
        menu_text = self.font_small.render("メニューに戻る", True, GameConstants.COLOR_WHITE)
        self.screen.blit(menu_text, (width - 190, 70))
    
    def _draw_button(self, color, y, text):
        """ボタンの描画"""
        pygame.draw.rect(self.screen, color, 
                        (self._center_x() - 150, y, GameConstants.BUTTON_WIDTH, GameConstants.BUTTON_HEIGHT))
        button_text = self.font_medium.render(text, True, GameConstants.COLOR_BLACK)
        self._center_blit(button_text, y + 5)
    
    def _center_x(self):
        """画面中央のX座標を取得"""
        return self.screen.get_width() // 2
    
    def _center_blit(self, text_surface, y):
        """テキストを水平方向中央に描画"""
        self.screen.blit(text_surface, 
                        (self._center_x() - text_surface.get_width() // 2, y))


# ======================
# ゲームマネージャー
# ======================
class GameManager:
    """ゲーム全体の管理"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GameConstants.DEFAULT_WIDTH, 
                                               GameConstants.DEFAULT_HEIGHT))
        pygame.display.set_caption("音階神経衰弱")
        
        self.renderer = GameRenderer(self.screen)
        self.card_count = GameConstants.CARD_COUNT_4X4
        self.time_limit = GameConstants.DEFAULT_TIME_LIMIT
        self.game_state = None
        
        self.current_scene = "menu"  # menu, time_adjustment, game
        self.running = True
        self.waiting_for_flip = False
        self.flip_wait_time = 0
    
    def run(self):
        """メインゲームループ"""
        while self.running:
            if self.current_scene == "menu":
                self._handle_menu()
            elif self.current_scene == "time_adjustment":
                self._handle_time_adjustment()
            elif self.current_scene == "game":
                self._handle_game()
    
    def _handle_menu(self):
        """メニュー画面の処理"""
        self.renderer.draw_menu(self.card_count, self.time_limit)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                center_x = self.screen.get_width() // 2
                
                if center_x - 150 < mx < center_x + 150:
                    if 200 < my < 240:
                        self.card_count = GameConstants.CARD_COUNT_4X4
                    elif 250 < my < 290:
                        self.card_count = GameConstants.CARD_COUNT_6X6
                    elif 340 < my < 380:
                        self.current_scene = "time_adjustment"
                    elif 400 < my < 450:
                        self._start_game()
    
    def _handle_time_adjustment(self):
        """時間調整画面の処理"""
        self.renderer.draw_time_adjustment(self.time_limit)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                center_x = self.screen.get_width() // 2
                
                if 250 < my < 300:
                    if center_x - 150 < mx < center_x - 100:
                        self.time_limit = max(GameConstants.MIN_TIME_LIMIT, 
                                            self.time_limit - GameConstants.TIME_ADJUST_STEP)
                    elif center_x + 100 < mx < center_x + 150:
                        self.time_limit = min(GameConstants.MAX_TIME_LIMIT, 
                                            self.time_limit + GameConstants.TIME_ADJUST_STEP)
                elif 350 < my < 400 and center_x - 100 < mx < center_x + 100:
                    self.current_scene = "menu"
    
    def _handle_game(self):
        """ゲーム画面の処理"""
        # 待機中の処理
        if self.waiting_for_flip:
            if time.time() - self.flip_wait_time > 0.5:
                self.game_state.reset_unmatched_cards()
                self.waiting_for_flip = False
        
        # タイムアップチェック
        if self.game_state.is_time_up() and not self.game_state.game_paused:
            self._end_game()
            return
        
        # ゲームクリアチェック
        if self.game_state.is_game_complete():
            self._end_game()
            return
        
        # 描画
        self.renderer.draw_game(self.game_state)
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.waiting_for_flip:
                self._handle_game_click(pygame.mouse.get_pos())
    
    def _handle_game_click(self, pos):
        """ゲーム中のクリック処理"""
        mx, my = pos
        width = self.screen.get_width()
        
        # 一時停止ボタン
        if width - 100 < mx < width - 50 and 10 < my < 50:
            self.game_state.toggle_pause()
            return
        
        # メニュー戻るボタン（ポーズ中のみ）
        if self.game_state.game_paused and width - 200 < mx < width - 50 and 60 < my < 100:
            self.current_scene = "menu"
            return
        
        # カードクリック
        if not self.game_state.game_paused:
            for i, (x, y) in enumerate(self.game_state.card_positions):
                if x < mx < x + GameConstants.CARD_SIZE and y < my < y + GameConstants.CARD_SIZE:
                    self.game_state.flip_card(i)
                    
                    # 2枚選択されたらマッチチェック
                    if len(self.game_state.selected_cards) == 2:
                        match_result = self.game_state.check_match()
                        if match_result is False:
                            self.waiting_for_flip = True
                            self.flip_wait_time = time.time()
                    break
    
    def _start_game(self):
        """ゲームを開始"""
        self.game_state = GameState(self.card_count, self.time_limit)
        self._adjust_screen_size()
        self.current_scene = "game"
    
    def _adjust_screen_size(self):
        """カード数に応じて画面サイズを調整"""
        grid_size = int(self.card_count ** 0.5)
        width = max(GameConstants.DEFAULT_WIDTH, 
                   (GameConstants.CARD_SIZE + GameConstants.CARD_GAP) * grid_size + 100)
        height = max(GameConstants.DEFAULT_HEIGHT, 
                    (GameConstants.CARD_SIZE + GameConstants.CARD_GAP) * grid_size + 160)
        self.screen = pygame.display.set_mode((width, height))
        self.renderer = GameRenderer(self.screen)
    
    def _end_game(self):
        """ゲーム終了処理"""
        self.renderer.draw_game_over(self.screen.get_width(), self.screen.get_height())
        pygame.time.wait(2000)
        self.current_scene = "menu"
        self.screen = pygame.display.set_mode((GameConstants.DEFAULT_WIDTH, 
                                               GameConstants.DEFAULT_HEIGHT))
        self.renderer = GameRenderer(self.screen)
    
    def quit(self):
        """ゲームを終了"""
        pygame.quit()


# ======================
# メイン実行
# ======================
def main():
    game = GameManager()
    game.run()
    game.quit()


if __name__ == "__main__":
    main()
