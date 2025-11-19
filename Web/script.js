// ======================================
// 定数定義
// ======================================
const GameConstants = {
    // カード設定
    CARD_COUNT_4X4: 16,
    CARD_COUNT_6X6: 36,
    
    // 時間設定
    DEFAULT_TIME_LIMIT: 60,
    MIN_TIME_LIMIT: 10,
    MAX_TIME_LIMIT: 300,
    TIME_ADJUST_STEP: 10,
    
    // 音設定
    SAMPLE_RATE: 44100,
    TONE_DURATION: 0.3,
    TONE_AMPLITUDE: 0.3,
    
    // カード表示時間
    CARD_FLIP_DELAY: 500,
    GAME_OVER_DELAY: 2000
};

// 音階の定義（周波数）
const NOTE_FREQUENCIES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25
};

// ======================================
// 音声再生クラス
// ======================================
class AudioPlayer {
    constructor() {
        this.audioContext = null;
        this.initAudioContext();
    }
    
    initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn("Web Audio API not supported", e);
        }
    }
    
    playTone(frequency, duration = GameConstants.TONE_DURATION) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(GameConstants.TONE_AMPLITUDE, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }
}

// ======================================
// カードデッキクラス
// ======================================
class CardDeck {
    constructor(numCards) {
        this.numCards = numCards;
        this.cards = this.shuffle();
    }
    
    shuffle() {
        const notes = Object.keys(NOTE_FREQUENCIES);
        const deck = [];
        
        for (let i = 0; i < this.numCards / 2; i++) {
            const note = notes[i % notes.length];
            deck.push(note, note);
        }
        
        // Fisher-Yates shuffle
        for (let i = deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [deck[i], deck[j]] = [deck[j], deck[i]];
        }
        
        return deck;
    }
    
    getCard(index) {
        return this.cards[index];
    }
    
    get length() {
        return this.cards.length;
    }
}

// ======================================
// ゲーム状態管理クラス
// ======================================
class GameState {
    constructor(cardCount, timeLimit) {
        this.cardCount = cardCount;
        this.timeLimit = timeLimit;
        this.deck = new CardDeck(cardCount);
        this.cardStates = new Array(cardCount).fill('hidden');
        this.selectedCards = [];
        this.matchesFound = 0;
        this.startTime = Date.now();
        this.gamePaused = false;
        this.pauseStartTime = 0;
        this.pausedTime = 0;
        this.timerInterval = null;
    }
    
    getElapsedTime() {
        if (this.gamePaused) {
            return (this.pauseStartTime - this.startTime - this.pausedTime) / 1000;
        }
        return (Date.now() - this.startTime - this.pausedTime) / 1000;
    }
    
    getTimeLeft() {
        return Math.max(0, this.timeLimit - this.getElapsedTime());
    }
    
    togglePause() {
        if (!this.gamePaused) {
            this.gamePaused = true;
            this.pauseStartTime = Date.now();
        } else {
            this.gamePaused = false;
            this.pausedTime += Date.now() - this.pauseStartTime;
        }
    }
    
    flipCard(index) {
        if (this.cardStates[index] === 'hidden' && this.selectedCards.length < 2) {
            this.cardStates[index] = 'flipped';
            this.selectedCards.push(index);
            return true;
        }
        return false;
    }
    
    checkMatch() {
        if (this.selectedCards.length === 2) {
            const [idx1, idx2] = this.selectedCards;
            if (this.deck.getCard(idx1) === this.deck.getCard(idx2)) {
                this.cardStates[idx1] = 'matched';
                this.cardStates[idx2] = 'matched';
                this.matchesFound++;
                this.selectedCards = [];
                return true;
            }
            return false;
        }
        return null;
    }
    
    resetUnmatchedCards() {
        for (const idx of this.selectedCards) {
            this.cardStates[idx] = 'hidden';
        }
        this.selectedCards = [];
    }
    
    isGameComplete() {
        return this.matchesFound === this.deck.length / 2;
    }
    
    isTimeUp() {
        return this.getTimeLeft() <= 0;
    }
}

// ======================================
// ゲームマネージャークラス
// ======================================
class GameManager {
    constructor() {
        this.audioPlayer = new AudioPlayer();
        this.gameState = null;
        this.cardCount = GameConstants.CARD_COUNT_4X4;
        this.timeLimit = GameConstants.DEFAULT_TIME_LIMIT;
        this.currentScene = 'menu';
        this.waitingForFlip = false;
        
        this.initElements();
        this.attachEventListeners();
        this.showScene('menu');
    }
    
    initElements() {
        // 画面要素
        this.screens = {
            menu: document.getElementById('menu-screen'),
            timeAdjustment: document.getElementById('time-adjustment-screen'),
            game: document.getElementById('game-screen'),
            gameOver: document.getElementById('game-over-screen')
        };
        
        // メニュー要素
        this.menuElements = {
            btn4x4: document.getElementById('btn-4x4'),
            btn6x6: document.getElementById('btn-6x6'),
            btnAdjustTime: document.getElementById('btn-adjust-time'),
            btnStart: document.getElementById('btn-start'),
            timeDisplay: document.getElementById('time-display')
        };
        
        // 時間調整要素
        this.adjustmentElements = {
            btnDecrease: document.getElementById('btn-decrease'),
            btnIncrease: document.getElementById('btn-increase'),
            btnConfirm: document.getElementById('btn-confirm'),
            currentTimeLimit: document.getElementById('current-time-limit'),
            adjustTimeValue: document.getElementById('adjust-time-value')
        };
        
        // ゲーム要素
        this.gameElements = {
            scoreDisplay: document.getElementById('score-display'),
            timeLeftDisplay: document.getElementById('time-left-display'),
            btnPause: document.getElementById('btn-pause'),
            btnReturnMenu: document.getElementById('btn-return-menu'),
            gameBoard: document.getElementById('game-board')
        };
    }
    
    attachEventListeners() {
        // メニュー画面
        this.menuElements.btn4x4.addEventListener('click', () => this.selectCardCount(16));
        this.menuElements.btn6x6.addEventListener('click', () => this.selectCardCount(36));
        this.menuElements.btnAdjustTime.addEventListener('click', () => this.showTimeAdjustment());
        this.menuElements.btnStart.addEventListener('click', () => this.startGame());
        
        // 時間調整画面
        this.adjustmentElements.btnDecrease.addEventListener('click', () => this.adjustTime(-GameConstants.TIME_ADJUST_STEP));
        this.adjustmentElements.btnIncrease.addEventListener('click', () => this.adjustTime(GameConstants.TIME_ADJUST_STEP));
        this.adjustmentElements.btnConfirm.addEventListener('click', () => this.confirmTimeAdjustment());
        
        // ゲーム画面
        this.gameElements.btnPause.addEventListener('click', () => this.togglePause());
        this.gameElements.btnReturnMenu.addEventListener('click', () => this.returnToMenu());
    }
    
    selectCardCount(count) {
        this.cardCount = count;
        this.menuElements.btn4x4.classList.toggle('selected', count === 16);
        this.menuElements.btn6x6.classList.toggle('selected', count === 36);
    }
    
    showTimeAdjustment() {
        this.adjustmentElements.currentTimeLimit.textContent = this.timeLimit;
        this.adjustmentElements.adjustTimeValue.textContent = this.timeLimit;
        this.showScene('timeAdjustment');
    }
    
    adjustTime(delta) {
        this.timeLimit = Math.max(
            GameConstants.MIN_TIME_LIMIT,
            Math.min(GameConstants.MAX_TIME_LIMIT, this.timeLimit + delta)
        );
        this.adjustmentElements.currentTimeLimit.textContent = this.timeLimit;
        this.adjustmentElements.adjustTimeValue.textContent = this.timeLimit;
    }
    
    confirmTimeAdjustment() {
        this.menuElements.timeDisplay.textContent = this.timeLimit;
        this.showScene('menu');
    }
    
    startGame() {
        this.gameState = new GameState(this.cardCount, this.timeLimit);
        this.setupGameBoard();
        this.showScene('game');
        this.startGameLoop();
    }
    
    setupGameBoard() {
        const board = this.gameElements.gameBoard;
        board.innerHTML = '';
        
        // グリッドクラスを設定
        board.className = 'game-board';
        if (this.cardCount === 16) {
            board.classList.add('grid-4x4');
        } else {
            board.classList.add('grid-6x6');
        }
        
        // カードを生成
        for (let i = 0; i < this.cardCount; i++) {
            const card = document.createElement('div');
            card.className = 'card';
            card.dataset.index = i;
            card.addEventListener('click', () => this.handleCardClick(i));
            board.appendChild(card);
        }
    }
    
    handleCardClick(index) {
        if (this.waitingForFlip || this.gameState.gamePaused) return;
        if (this.gameState.selectedCards.length >= 2) return;
        if (this.gameState.cardStates[index] !== 'hidden') return;
        
        // カードをめくる
        if (this.gameState.flipCard(index)) {
            const note = this.gameState.deck.getCard(index);
            this.audioPlayer.playTone(NOTE_FREQUENCIES[note]);
            this.updateCardDisplay(index);
            
            // 2枚選択されたらマッチチェック
            if (this.gameState.selectedCards.length === 2) {
                this.waitingForFlip = true;
                
                setTimeout(() => {
                    const matchResult = this.gameState.checkMatch();
                    
                    if (matchResult === false) {
                        this.gameState.resetUnmatchedCards();
                    }
                    
                    this.updateAllCards();
                    this.waitingForFlip = false;
                    
                    // ゲーム完了チェック
                    if (this.gameState.isGameComplete()) {
                        this.endGame();
                    }
                }, GameConstants.CARD_FLIP_DELAY);
            }
        }
    }
    
    updateCardDisplay(index) {
        const cards = this.gameElements.gameBoard.querySelectorAll('.card');
        const card = cards[index];
        const state = this.gameState.cardStates[index];
        
        card.className = 'card';
        
        if (state === 'flipped' || state === 'matched') {
            card.classList.add(state);
            const note = this.gameState.deck.getCard(index);
            card.textContent = note;
        } else {
            card.textContent = '';
        }
    }
    
    updateAllCards() {
        for (let i = 0; i < this.cardCount; i++) {
            this.updateCardDisplay(i);
        }
    }
    
    startGameLoop() {
        this.gameState.timerInterval = setInterval(() => {
            if (this.gameState.gamePaused) return;
            
            this.updateGameStatus();
            
            if (this.gameState.isTimeUp()) {
                this.endGame();
            }
        }, 100);
    }
    
    updateGameStatus() {
        this.gameElements.scoreDisplay.textContent = `スコア: ${this.gameState.matchesFound}`;
        this.gameElements.timeLeftDisplay.textContent = `残り時間: ${this.gameState.getTimeLeft().toFixed(1)}`;
    }
    
    togglePause() {
        this.gameState.togglePause();
        this.gameElements.btnPause.classList.toggle('paused', this.gameState.gamePaused);
        this.gameElements.btnReturnMenu.classList.toggle('hidden', !this.gameState.gamePaused);
    }
    
    returnToMenu() {
        if (this.gameState && this.gameState.timerInterval) {
            clearInterval(this.gameState.timerInterval);
        }
        this.showScene('menu');
    }
    
    endGame() {
        if (this.gameState.timerInterval) {
            clearInterval(this.gameState.timerInterval);
        }
        
        this.showScene('gameOver');
        
        setTimeout(() => {
            this.showScene('menu');
        }, GameConstants.GAME_OVER_DELAY);
    }
    
    showScene(sceneName) {
        this.currentScene = sceneName;
        
        for (const [name, screen] of Object.entries(this.screens)) {
            screen.classList.toggle('active', name === sceneName);
        }
    }
}

// ======================================
// 初期化
// ======================================
document.addEventListener('DOMContentLoaded', () => {
    new GameManager();
});
