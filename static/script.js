// DOM 요소 가져오기
const textToType = document.getElementById("text-to-type");
const typingInput = document.getElementById("typing-input");
const speedDisplay = document.getElementById("speed");
const accuracyDisplay = document.getElementById("accuracy");
const highScoreDisplay = document.getElementById("high-score");
const resetHighScoreButton = document.getElementById("reset-high-score");
const highScoreMessage = document.getElementById("high-score-message");

// 타이핑 연습 텍스트
typingTexts = [
    'print("Hello, World!")',
    'print("hello")',
    'print(5)',
    'print(10)',
    'print(-1)',
    'print(2+3)',
    'print(10-20)',
    'print(5*2)',
    'print(10//2)',
    'print("파이썬")',
    'a=1',
    'a=10',
    'a="파이썬"',
    'word="파이썬"',
    'c = a + b',
    'c = a - b',
    'for i in range(10):',
    'if x > 0:',
    'while True:',
    'input("Enter a number: ")',
    'input()',
    'a=input()',
    'pw = input()',
    'ID = input()',
    'print("피자","타코","파스타")',
    'import math',
    'a = [1, 2, 3]',
    'b = {"key":"value"}',
    'print(a[0])',
    'for i in range(1, 11):',
    'print(i ** 2)',
    'if a == b:',
    'elif x < 0:',
    'else:',
    'def func():',
    'return x * y',
    'try:',
    'print("Python is fun!")',
    'a, b = 5, 10',
    'a += b',
    'print("Sum:", a)',
    'del a[0]',
    'print(sqrt(16))',
    'x = 10',
    'y = x / 3',
    'print(round(y, 2))',
    '"Hello".upper()',
    '"World".lower()',
    '"Hello" + " " + "World"',
    'len("Python")',
    'max([1, 2, 3])',
    'min([1, 2, 3])',
    'sum([1, 2, 3])',
    'sorted([3, 1, 2])',
    'list(range(5))',
    'x = None',
    'if x is None:',
    'a = True',
    'b = False',
    'not a',
    'a and b',
    'a or b',
    'str(123)',
    'int("456")',
    'float("3.14")',
    'x = [0 for i in range(5)]',
    'print("Done")',
    'print(i, val)',
    'print(e)',
    '"abc".replace("a", "z")',
    'x = {1, 2, 3}',
    'round(3.14159, 2)',
    'bin(255)',
    'hex(255)',
    'oct(255)',
    'b = [4, 5, 6]',
    'd = {"name":"John", "age":30}',
    'print(key, value)',
    '"Python"[::-1]',
    'print(list_a[1])',
    'print(a[1])',
    'print(b[2])',
    'a_list[-1]',
    'print(a[1:4])',
    'print(a[-5:-1])',
    'print(all[:])',
    'print(front[1:])',
    'print(end[:9])',
    'len',
    'import random',
    'import os',
]


// 소리 재생 함수
function playSound(type) {
    const audio = new Audio(type === "correct" ? "/static/correct.mp3" : "/static/incorrect.mp3");
    audio.play();
}

// 초기 상태 변수
let currentText = "";
let startTime = null;


// 최고 기록 초기화 및 로드
function loadHighScore() {
    const highScore = localStorage.getItem("highScore") || 0;
    highScoreDisplay.textContent = highScore;
}

function resetHighScore() {
    localStorage.removeItem("highScore");
    highScoreDisplay.textContent = 0;
}

resetHighScoreButton.addEventListener("click", resetHighScore);


// 연습 텍스트 초기화
function initializeText() {
    const randomIndex = Math.floor(Math.random() * typingTexts.length);
    currentText = typingTexts[randomIndex];
    textToType.textContent = currentText;
    typingInput.value = "";
    startTime = null;
    updateStats(0, 0, true);
}

// 통계 업데이트 함수
function updateStats(speed, accuracy, isSyntaxValid) {
    speedDisplay.textContent = speed;
    accuracyDisplay.textContent = `${accuracy}% (문법${isSyntaxValid ? 'O' : ' 오류O'})`;
}

// 서버에 코드 검증 요청
async function validateCode(userInput) {
    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_code: userInput,
                correct_code: currentText
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return { 
            is_correct: false, 
            is_syntax_valid: false, 
            accuracy: 0 
        };
    }
}



// 최고 기록 갱신 알림 메시지 표시 함수
function showHighScoreMessage() {
    highScoreMessage.style.display = "inline";
    highScoreMessage.style.animation = "fadeOut 2s ease-in-out forwards";

    // 3초 후에 메시지 숨기기
    setTimeout(() => {
        highScoreMessage.style.display = "none";
    }, 3000);
}


// 최고 기록 갱신 함수
function updateHighScore(speed) {
    const highScore = parseInt(localStorage.getItem("highScore"), 10) || 0;

    if (speed > highScore) {
        localStorage.setItem("highScore", speed);
        highScoreDisplay.textContent = speed;
        
        // 알림 메시지 표시
        showHighScoreMessage();
    }
}


// 정답 처리
function handleCorrect(speed) {
    playSound("correct");
    typingInput.style.borderColor = "#4CAF50";
    updateHighScore(speed); // 정답 시 최고 기록 갱신
    setTimeout(() => {
        initializeText();
        typingInput.focus();
    }, 100);
}

// 오답 처리
function handleIncorrect() {
    playSound("incorrect");
    typingInput.style.borderColor = "#FF4C4C";
}

// 실시간 입력 검증
let validationTimeout = null;

// 입력 이벤트 처리
typingInput.addEventListener("input", async () => {
    if (!startTime) startTime = new Date();
    
    if (validationTimeout) {
        clearTimeout(validationTimeout);
    }
    
    validationTimeout = setTimeout(async () => {
        const userInput = typingInput.value;
        const validation = await validateCode(userInput);
        
        const elapsedTime = (new Date() - startTime) / 1000 / 60;
        const charactersTyped = userInput.length;
        const speed = Math.round((charactersTyped / elapsedTime) || 0);
        
        updateStats(speed, validation.accuracy, validation.is_syntax_valid);
        
        // 정답 체크
        if (validation.is_correct) {
            handleCorrect(speed);
        }
    }, 100);
});

// Enter 키 입력 처리
typingInput.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
        const userInput = typingInput.value;
        const validation = await validateCode(userInput);
        
        if (!validation.is_correct) {
            handleIncorrect();
            typingInput.value = "";
        }
        
        event.preventDefault();
    }
});

// 초기화
initializeText();
loadHighScore();