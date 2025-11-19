import pygame
import numpy as np
import sounddevice as sd
import random
import time
import os

# 音の再生関数
def play_tone(frequency=440, duration=1.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(wave, samplerate=sample_rate)
    sd.wait()

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

# カードをシャッフルして、ペアを作成
def shuffle_deck(num_cards):
    notes = list(NOTE_FREQUENCIES.keys()) * (num_cards // 2)
    random.shuffle(notes)  # シャッフル
    return notes

# 日本語対応フォントの設定
def get_font(size):
    # システムにインストールされているフォントを使用
    available_fonts = pygame.font.get_fonts()
    
    # 日本語フォントの候補リスト (優先順)
    japanese_font_candidates = [
        'msgothic', 'meiryo', 'yumin',   # Windows
        'hiragino maru gothic pron', 'hiragino kaku gothic pron',  # Mac
        'noto sans cjk jp', 'noto sans jp', 'noto serif jp',  # Linux
        'ms gothic', 'yu gothic', 'yu mincho'  # その他一般的なフォント
    ]
    
    # 利用可能な日本語フォントを検索
    for font_name in japanese_font_candidates:
        for available_font in available_fonts:
            if font_name in available_font.lower():
                return pygame.font.SysFont(font_name, size)
    
    # 日本語フォントが見つからない場合はデフォルトフォントを使用
    try:
        # フォントファイルが特定の場所にある場合（例：実行ファイルと同じディレクトリ）
        font_path = os.path.join(os.path.dirname(__file__), "font.ttf")
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
    except:
        pass
    
    # それでも見つからない場合はデフォルトフォントを使用
    return pygame.font.Font(None, size)

# メニュー画面の描画
def draw_menu():
    screen.fill((255, 255, 255))  # 背景を白に
    title_font = get_font(42)  # 48から42に縮小
    menu_font = get_font(28)   # 36から28に縮小
    
    title_text = title_font.render("音階神経衰弱", True, (0, 0, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    
    # 4x4盤面の選択ボタン (選択中は緑、それ以外は通常の背景色)
    button_4x4_color = (0, 180, 0) if card_count == 16 else (220, 220, 220)
    pygame.draw.rect(screen, button_4x4_color, (WIDTH // 2 - 150, 200, 300, 40))
    text_4x4 = menu_font.render("4x4 (16カード)", True, (0, 0, 0))
    screen.blit(text_4x4, (WIDTH // 2 - text_4x4.get_width() // 2, 205))
    
    # 6x6盤面の選択ボタン (選択中は緑、それ以外は通常の背景色)
    button_6x6_color = (0, 180, 0) if card_count == 36 else (220, 220, 220)
    pygame.draw.rect(screen, button_6x6_color, (WIDTH // 2 - 150, 250, 300, 40))
    text_6x6 = menu_font.render("6x6 (36カード)", True, (0, 0, 0))
    screen.blit(text_6x6, (WIDTH // 2 - text_6x6.get_width() // 2, 255))

    # 時間制限表示（ボタンとテキストを分離）
    time_limit_label = menu_font.render("時間制限:", True, (0, 0, 0))
    screen.blit(time_limit_label, (WIDTH // 2 - 150, 300))
    
    time_value = menu_font.render(f"{time_limit}秒", True, (0, 0, 0))
    screen.blit(time_value, (WIDTH // 2 + 50, 300))

    # 時間制限調整ボタン - より大きく、位置を調整
    pygame.draw.rect(screen, (0, 150, 0), (WIDTH // 2 - 100, 340, 200, 40))
    time_adjust_text = menu_font.render("時間を調整", True, (255, 255, 255))
    screen.blit(time_adjust_text, (WIDTH // 2 - time_adjust_text.get_width() // 2, 345))

    # 開始ボタン
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH // 2 - 100, 400, 200, 50))
    start_text = menu_font.render("開始", True, (255, 255, 255))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 410))

    pygame.display.flip()

# 時間制限調整画面の描画
def draw_time_adjustment():
    screen.fill((255, 255, 255))  # 背景を白に
    title_font = get_font(42)  # 48から42に縮小
    menu_font = get_font(28)   # 36から28に縮小
    
    title_text = title_font.render("時間制限の調整", True, (0, 0, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    
    time_text = menu_font.render(f"現在の時間制限: {time_limit}秒", True, (0, 0, 0))
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 200))
    
    # 減少ボタン
    pygame.draw.rect(screen, (200, 0, 0), (WIDTH // 2 - 150, 250, 50, 50))
    minus_text = menu_font.render("-", True, (255, 255, 255))  # titleフォントからmenuフォントに変更
    screen.blit(minus_text, (WIDTH // 2 - 135, 260))
    
    # 現在の値
    value_text = menu_font.render(f"{time_limit}", True, (0, 0, 0))  # titleフォントからmenuフォントに変更
    screen.blit(value_text, (WIDTH // 2 - value_text.get_width() // 2, 260))
    
    # 増加ボタン
    pygame.draw.rect(screen, (0, 200, 0), (WIDTH // 2 + 100, 250, 50, 50))
    plus_text = menu_font.render("+", True, (255, 255, 255))  # titleフォントからmenuフォントに変更
    screen.blit(plus_text, (WIDTH // 2 + 117, 260))
    
    # 確定ボタン
    pygame.draw.rect(screen, (0, 0, 200), (WIDTH // 2 - 100, 350, 200, 50))
    confirm_text = menu_font.render("確定", True, (255, 255, 255))
    screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, 365))
    
    pygame.display.flip()

# ゲームの進行状況（スコア・タイマー）も修正
def draw_game_status(score, time_left):
    game_font = get_font(28)  # 36から28に縮小
    
    # スコアの表示
    score_text = game_font.render(f"スコア: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    
    # 残り時間の表示 - 文字が重ならないようにX位置を調整
    time_text = game_font.render(f"残り時間: {time_left:.1f}", True, (0, 0, 0))
    # 小数点以下1桁に制限して文字数を減らす
    screen.blit(time_text, (WIDTH - 250, 10))

# 時間制限調整画面の描画
def draw_time_adjustment():
    screen.fill((255, 255, 255))  # 背景を白に
    title_font = get_font(48)
    menu_font = get_font(36)
    
    title_text = title_font.render("時間制限の調整", True, (0, 0, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    
    time_text = menu_font.render(f"現在の時間制限: {time_limit}秒", True, (0, 0, 0))
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 200))
    
    # 減少ボタン
    pygame.draw.rect(screen, (200, 0, 0), (WIDTH // 2 - 150, 250, 50, 50))
    minus_text = title_font.render("-", True, (255, 255, 255))
    screen.blit(minus_text, (WIDTH // 2 - 135, 260))
    
    # 現在の値
    value_text = title_font.render(f"{time_limit}", True, (0, 0, 0))
    screen.blit(value_text, (WIDTH // 2 - value_text.get_width() // 2, 260))
    
    # 増加ボタン
    pygame.draw.rect(screen, (0, 200, 0), (WIDTH // 2 + 100, 250, 50, 50))
    plus_text = title_font.render("+", True, (255, 255, 255))
    screen.blit(plus_text, (WIDTH // 2 + 117, 260))
    
    # 確定ボタン
    pygame.draw.rect(screen, (0, 0, 200), (WIDTH // 2 - 100, 350, 200, 50))
    confirm_text = menu_font.render("確定", True, (255, 255, 255))
    screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, 365))
    
    pygame.display.flip()

# ゲームの進行状況（スコア・タイマー）
def draw_game_status(score, time_left):
    game_font = get_font(36)
    
    # スコアの表示
    score_text = game_font.render(f"スコア: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    
    # 残り時間の表示 - カードに隠れないように上側に表示
    time_text = game_font.render(f"残り時間: {time_left:.2f}", True, (0, 0, 0))
    screen.blit(time_text, (WIDTH - 300, 10))

# ゲームの設定
def start_game(card_count):
    global cards, card_positions, card_states, card_values, selected_cards, matches_found, start_time, running, game_paused, pause_start_time
    
    cards = shuffle_deck(card_count)
    
    if card_count == 16:
        # カードが上部に近すぎないように、少し下に移動
        card_positions = [(x * (CARD_SIZE + CARD_GAP), y * (CARD_SIZE + CARD_GAP) + 60) for y in range(4) for x in range(4)]
    elif card_count == 36:
        card_positions = [(x * (CARD_SIZE + CARD_GAP), y * (CARD_SIZE + CARD_GAP) + 60) for y in range(6) for x in range(6)]
    
    # 画面サイズの調整
    global WIDTH, HEIGHT
    WIDTH = max(600, (CARD_SIZE + CARD_GAP) * (int(card_count ** 0.5)) + 100)  # 最大で600pxより広く
    HEIGHT = max(600, (CARD_SIZE + CARD_GAP) * (int(card_count ** 0.5)) + 160)  # 上部にスペースを追加
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # 画面サイズを再設定
    
    card_states = ["hidden"] * len(cards)
    card_values = [None] * len(cards)
    selected_cards = []
    matches_found = 0
    start_time = time.time()  # ゲーム開始時刻
    game_paused = False  # 一時停止状態
    pause_start_time = 0  # 一時停止開始時間

# ゲーム終了後のメニューに戻る
def end_game():
    end_font = get_font(48)
    game_over_text = end_font.render("ゲーム終了！おめでとう！", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2000)  # 2秒後にメニュー画面に戻る

# 初期化
pygame.init()

# 初期画面設定
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("音階神経衰弱")

# ゲームの設定
CARD_SIZE = 100
CARD_GAP = 10
time_limit = 60  # デフォルトの時間制限（秒）

# メニュー画面表示
show_menu = True
show_time_adjustment = False  # 時間調整画面表示フラグ
running = True
game_started = False
card_count = 16  # デフォルトのカード数（4x4）
game_paused = False  # 一時停止フラグ
pause_button_color = (255, 0, 0)  # 初期のPauseボタンの色は赤
pause_start_time = 0  # 一時停止開始時間
paused_time = 0  # 一時停止した累積時間

while running:
    if show_menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # 盤面選択ボタンの領域判定を改善
                if WIDTH // 2 - 150 < mx < WIDTH // 2 + 150:
                    if 200 < my < 240:  # 4x4カードを選択
                        card_count = 16
                    elif 250 < my < 290:  # 6x6カードを選択
                        card_count = 36
                    elif 300 < my < 340:  # 時間制限調整ボタン
                        show_menu = False
                        show_time_adjustment = True
                    elif 400 < my < 450:  # 開始ボタン
                        show_menu = False
                        start_game(card_count)
    
    elif show_time_adjustment:
        draw_time_adjustment()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 250 < my < 300:
                    if WIDTH // 2 - 150 < mx < WIDTH // 2 - 100:  # マイナスボタン
                        time_limit = max(10, time_limit - 10)  # 最低10秒まで
                    elif WIDTH // 2 + 100 < mx < WIDTH // 2 + 150:  # プラスボタン
                        time_limit = min(300, time_limit + 10)  # 最大300秒まで
                elif 350 < my < 400 and WIDTH // 2 - 100 < mx < WIDTH // 2 + 100:  # 確定ボタン
                    show_time_adjustment = False
                    show_menu = True
    
    else:
        # ゲーム進行
        screen.fill((255, 255, 255))  # 背景を白に
        
        # タイマーの計算 - ポーズ時間を考慮
        if game_paused:
            elapsed_time = pause_start_time - start_time - paused_time
        else:
            elapsed_time = time.time() - start_time - paused_time
            
        time_left = max(0, time_limit - elapsed_time)  # 残り時間を設定した時間制限から減算

        if time_left == 0 and not game_paused:
            end_game()  # タイムアップ
            show_menu = True  # メニュー画面に戻る

        draw_game_status(matches_found, time_left)  # スコアと残り時間の表示

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # ゲーム一時停止ボタン
                if WIDTH - 100 < mx < WIDTH - 50 and 10 < my < 50:
                    if not game_paused:
                        # ポーズを開始
                        game_paused = True
                        pause_start_time = time.time()
                        pause_button_color = (0, 0, 255)  # 青色に変更
                    else:
                        # ポーズを解除
                        game_paused = False
                        paused_time += time.time() - pause_start_time  # 一時停止した時間を累積
                        pause_button_color = (255, 0, 0)  # 赤色に戻す
                    continue  # 一時停止ボタンが押された場合、他の処理をスキップ
                
                # メニューに戻るボタン（ポーズ中のみ表示・機能）
                if game_paused and WIDTH - 200 < mx < WIDTH - 50 and 60 < my < 100:
                    show_menu = True
                    game_paused = False
                    pause_button_color = (255, 0, 0)  # 赤色に戻す
                    continue

                # クリックされたカードを探す
                if not game_paused:
                    for i, (x, y) in enumerate(card_positions):
                        if x < mx < x + CARD_SIZE and y < my < y + CARD_SIZE:
                            if card_states[i] == "hidden":
                                card_states[i] = "flipped"
                                selected_cards.append(i)
                                play_tone(NOTE_FREQUENCIES[cards[i]])

                    # 2枚選択された場合の処理
                    if len(selected_cards) == 2:
                        if cards[selected_cards[0]] == cards[selected_cards[1]]:
                            matches_found += 1
                            card_values[selected_cards[0]] = cards[selected_cards[0]]
                            card_values[selected_cards[1]] = cards[selected_cards[1]]
                        else:
                            pygame.time.wait(500)  # 少し待ってから裏返す
                            card_states[selected_cards[0]] = "hidden"
                            card_states[selected_cards[1]] = "hidden"
                        selected_cards = []

        # カードの描画
        for i, (x, y) in enumerate(card_positions):
            if card_states[i] == "hidden":
                pygame.draw.rect(screen, (200, 200, 200), (x, y, CARD_SIZE, CARD_SIZE))
            else:
                pygame.draw.rect(screen, (0, 255, 0), (x, y, CARD_SIZE, CARD_SIZE))
                if card_values[i] is not None:
                    card_font = pygame.font.Font(None, 36)  # カードのテキストはアルファベットなのでデフォルトフォントでOK
                    note_text = card_font.render(card_values[i], True, (255, 255, 255))
                    screen.blit(note_text, (x + CARD_SIZE // 4, y + CARD_SIZE // 4))

        # 一時停止ボタンの描画
        pause_button = pygame.draw.rect(screen, pause_button_color, (WIDTH - 100, 50, 80, 40))
        pause_font = get_font(30)
        pause_text = pause_font.render("停止", True, (255, 255, 255))
        screen.blit(pause_text, (WIDTH - 80, 50))
        
        # メニューに戻るボタン（ポーズ中のみ表示）
        if game_paused:
            menu_button = pygame.draw.rect(screen, (50, 50, 200), (WIDTH - 200, 60, 150, 40))
            menu_font = get_font(30)
            menu_text = menu_font.render("メニューに戻る", True, (255, 255, 255))
            screen.blit(menu_text, (WIDTH - 190, 70))

        # ゲーム終了メッセージの表示
        if matches_found == len(cards) // 2:
            end_game()
            show_menu = True  # メニュー画面に戻る

    pygame.display.flip()

pygame.quit()