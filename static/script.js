// DOM 요소 가져오기
const textToType = document.getElementById("text-to-type");
const typingInput = document.getElementById("typing-input");
const speedDisplay = document.getElementById("speed");
const accuracyDisplay = document.getElementById("accuracy");
const highScoreDisplay = document.getElementById("high-score");
const resetHighScoreButton = document.getElementById("reset-high-score");
const highScoreMessage = document.getElementById("high-score-message");
const currentScoreDisplay = document.getElementById("current-score");
const averageScoreDisplay = document.getElementById("average-score");
let scoreHistory = [];


// 난이도 버튼들
const lvButtons = document.querySelectorAll(".level-buttons button");

// 타이핑 연습 텍스트
const typingTexts = {
    "lv0": ['1', '2', '3', '4', '5', '10', '99', '3.14', '1.414', '345', '456', '100', 
        'a', 'b', 'c', 'd', 'x', 'y', 'z', 'n', 'n1', 'n2', 'n3', 'lv0', 'Hi', 'Cat', 'Dog', 'dh', 'val',
        'num1', 'num2', 'num3', 'res', 'temp', 'cnt', 'swap', 'print', 'input', 
        'True', 'False', 'if', 'else', 'for', 'while', 'def', 'len', 'round', 'jingiru', 'donghwa', 'imun',
        'a=b', 'b=a', 'a + b', 'a - b', 'a * b', 'a / b', 'a ** b', 'a // b', 'n1+n2'],

    "lv1": [
        'print("Hello, World!")',
        'Algorithm',
        'print("hello","world!")',
        'print("hello")',
        'print("Hello")',
        'print("HELLO")',
        'print("hi")',
        'print("Hi")',
        'print("HI")',
        'print(5)',
        'print(10)',
        'print(100)',
        'print(99)',
        'print(3.14)',
        'print(-1)',
        'print(-5)',
        'print(-10)',
        'print(-5.5)',
        'print(10,20)',
        'print(100,-300)',
        'print(2+3)',
        'print(10-20)',
        'print(5*2)',
        'print("p"*2)',
        'print("pizza"*5)',
        'print("pizza" * 10)',
        'print("n" * 10)',
        'print("loop " * 10)',
        'print(10//2)',
        'print("파이썬")',
        'input("아이디를 입력하세요")',
        'input("비밀번호를 입력하세요")',
        'input("ID = ?")',
        'input("PW = ?")',
        'input("when?")',
        'input("where?")',
        'input("who?")',
        'a="파이썬"',
        'word="파이썬"',
        'c = a + b',
        'print(x * 2)',
        'c = a - b',
        'res = n1 + n2',
        'res=n1+n2',
        'temp=a',
        'temp = a',
        'a = b',
        'b = a',
        'c = a - b',
        'c = a + b',
        'res = num1+num2',
        'input("Enter a number: ")',
        'input()',
        'a=input()',
        'pw = input()',
        'ID = input()',
        'print("피자","타코","파스타")',
        'print(i ** 2)',
        'try:',
        'print("Python is fun!")',
        'a, b = 5, 10',
        'a += b',
        'print("Sum:", a)',
        'x = 10',
        'y = x / 3',
        'x = None',
        'a = True',
        'b = False',
        'not a',
        'a and b',
        'a or b',
        'str(123)',
        'str(3.14)',
        'str(50)',
        'int("456")',
        'int("10000")',
        'int("123456")',
        'bin(255)',
        'bin(100)',
        'bin(50)',
        'bin(1)',
        'hex(200)',
        'hex(255)',
        'hex(150)',
        'hex(20)',
        'oct(255)',
        'oct(135)',
        'oct(38)',
        'oct(81)',
        'float("3.14")',
        'print("Done")',
        'print(i, val)',
        'print(e)'
    ],

    "lv2": [
        'def add(a, b):',
        'return a + b',
        'x = ["a", "b", "c"]',
        'for i in x:',
        'print(i[0])',
        'print(i[1])',
        'print(b[-1])',
        'print(int("1"))',
        'print(max(a))',
        'print(min(b))',
        'print(max(list_a))',
        'print(min(list_B))',
        'print(list1[-1])',
        'for i in range(10):',
        'import math',
        'import random',
        'import time',
        'a = [1, 2, 3]',
        'b = {"key":"value"}',
        'for i in range(1, 11):',
        'print(a[0])',
        'if a == b:',
        'if a != b:',
        'if n1 == n2:',
        'if answer == "y":',
        'if answer == "n":',
        'elif answer == "n":',
        'elif x < 0:',
        'else:',
        'if x > 0:',
        'while True:',
        'def func():',
        'return x * y',
        '"Hello".upper()',
        '"World".lower()',
        'max([1, 2, 3])',
        'min([1, 2, 3])',
        'sum([1, 2, 3])',
        'sorted([3, 1, 2])',
        'if x is None:',
        'print(a[1])',
        'print(b[2])',
        'a_list[-1]',
        'print(a[1:4])',
        'print(all[:])',
        'print(front[1:])',
        'print(end[:9])',
        'del a[0]',
        'del b[1]',
        'print(sqrt(16))',
        'print(round(y, 2))',
        'len("Python")',
        'list(range(5))',
        'round(3.14159, 2)',
        'b = [4, 5, 6]',
        'print(key, value)',
        'import random',
        'import os',
        'int(input())'
    ],

    "lv3": [
        'a, b = input().split()',
        'stats = ["lv", "hp", "mp", "atk", "def"]',
        'data = [100, 200, 300, "cm", "inch"]',
        't1, t2 = input().split()',
        's1, s2 = input().split()',
        'id, pw = input().split()',
        'a, b = map(int, input().split())',
        'a, b = map(str, input().split())',
        'n1, n2 = map(int, input().split())',
        'a, b, c = map(int, input().split())',
        'list1 = list(map(int, input().split()))',
        'number = list(map(int, input().split()))',
        'if x[0] == 1:',
        'if x[-5] != 0:',
        'print(list_a[1])',
        'print(a[-5:-1])',
        '"Python"[::-1]',
        'x = {1, 2, 3}',
        'y = {4 ,5 ,6}',
        'a = {"key": "value"}',
        '"Hello" + " " + "World"',
        'd = {"name":"John", "age":30}',
        'x = [0 for i in range(5)]',
        '"abc".replace("a", "z")',
        'a = list(range(5, 15))',
        'a = {"apple": 5, "banana": 10, "cherry": 7}',
        'd = {"name": "Alice", "age": 25, "city": "Wonderland"}',
        'y = [x**2 for x in range(10)]',
        'y = math.pow(3, 2)',
        'z = math.ceil(4.2)',
        'x = math.floor(4.8)',
        'del a["key1"]',
        'x.append("orange")',
        'x.insert(1, "grape")',
        'x.index("a")',
        'x.remove("banana")'
    ],

    "lv4": [
        'print(s[::2] + s[1::2][::-1])',
        '"".join(sorted(set("banana")))',
        '"".join(["1" if i%2==0 else "0" for i in range(16)])',
        '",".join([str(i) for i in range(10, 0, -2)])',
        'zero = [0 for i in range(10)]',
        'print([i for i in range(100) if str(i)==str(i)[::-1]])',
        'print("짝수" if a%2==0 else "홀수")',
        'print("홀수" if a%2!=0 else "짝수")',
        'print("even" if num%2==0 else "odd")',
        'print("합격" if score>=std else "불합격")',
        'matrix = [[i*j for j in range(3)] for i in range(3)]',
        'chars = list("extreme!")',
        'var123 = list("!#@$#%$^%&^*&(*)")',
        'user["pw"] = "admin34!@"[1::2]',
        'info = {"name":"jin", "job":"teacher"}',
        'mix = list(zip(["a","b"], [1,2], [True, False]))',
        'col, row = input().split("-")',
        'message = "Hello Python".replace(" ", "-")',
        'nums = list(map(int, input().split(",")))',
        'print("".join(sorted(set("mississippi"))))',
        'colors = ["red", "green", "blue"]; colors.reverse()',
        'result = [i for i in range(20) if i%2 and i%3]',
        'output = "hello world".title().replace(" ", "_")',
        'len([w for w in input().split() if w.isdigit()])'
    ]

};


let currentLevel = "lv0"; // 기본 난이도
let previousIndex = -1; // 이전에 선택된 인덱스를 저장할 변수



// 페이지 로드 시, 기본 lv0 버튼에 border 추가
window.addEventListener("load", () => {
    const lv0Button = document.getElementById("lv0");
    lv0Button.style.border = "2.5px solid #FFD700"; // lv0 버튼에 기본 border 추가
    initializeText(); // 텍스트 초기화
});


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

    // 현재 및 평균 점수까지 초기화 (25.05.26 추가)
    scoreHistory = [];
    currentScoreDisplay.textContent = 0;
    averageScoreDisplay.textContent = 0;

    // 타이핑 속도 표시도 초기화
    speedDisplay.textContent = 0;
    accuracyDisplay.textContent = `0% (문법O)`;  // 명확하게 초기화
}

resetHighScoreButton.addEventListener("click", resetHighScore);


// 연습 텍스트 초기화
function initializeText() {
    let randomIndex;
    do {
        randomIndex = Math.floor(Math.random() * typingTexts[currentLevel].length);
    } while (randomIndex === previousIndex); // 이전 인덱스와 같으면 다시 선택
    
    previousIndex = randomIndex; // 현재 인덱스를 저장
    currentText = typingTexts[currentLevel][randomIndex];
    textToType.textContent = currentText;
    typingInput.value = "";
    startTime = null;
    accuracyDisplay.textContent = `0% (문법O)`;  // 또는 원하는 초기 텍스트
    typingInput.style.borderColor = ""; // 색 초기화
}

// 통계 업데이트 함수
function updateStats(speed, accuracy, isSyntaxValid) {
    // 기존 표시
    speedDisplay.textContent = speed;
    accuracyDisplay.textContent = `${accuracy}% (문법${isSyntaxValid ? 'O' : ' 오류O'})`;


    // 평균 점수 표시 (25.05.26 추가)
    if (speed > 0 && accuracy === 100 && isSyntaxValid) {
        scoreHistory.push(speed);
    }

    const sum = scoreHistory.reduce((a, b) => a + b, 0);
    const average = scoreHistory.length ? Math.round(sum / scoreHistory.length) : 0;
    averageScoreDisplay.textContent = average;
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

    // 현재 점수 표시 (25.05.26 추가)
    currentScoreDisplay.textContent = speed;

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

    const userInput = typingInput.value;

    if (/\s{3,}/.test(userInput)) {
        updateStats(0, 0, false);
        typingInput.style.borderColor = "#FF4C4C";
        accuracyDisplay.textContent = "부정 입력(무한 스페이스바) 감지";
        return;
    }

    // 🥚 이스터에그: 수행평가 입력 시 전환
    if (userInput.trim() === "수행평가") {
        window.location.href = "/exam";
        return;
    }
    
    if (validationTimeout) {
        clearTimeout(validationTimeout);
    }
    
    validationTimeout = setTimeout(async () => {
        const validation = await validateCode(userInput);
        
        const elapsedTime = (new Date() - startTime) / 1000 / 60;
        const charactersTyped = userInput.length;

        let speedFactor = 1;
        if (currentLevel === "lv0") speedFactor = 1.0;
        else if (currentLevel === "lv1") speedFactor = 0.95;
        else if (currentLevel === "lv2") speedFactor = 0.9;
        else if (currentLevel === "lv3") speedFactor = 0.85;
        else if (currentLevel === "lv4") speedFactor = 0.8;

        // 짧은 글자는 추가 가중치 (선택)
        if (currentText.length <= 3) {
            speedFactor += 0.05;
        }

        const speed = Math.round((charactersTyped / elapsedTime) * speedFactor);
        
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


// 난이도 버튼 클릭 시 텍스트 변경 및 버튼 상태 변경
lvButtons.forEach(button => {
    button.addEventListener("click", (e) => {
        currentLevel = e.target.id; // 현재 난이도 업데이트
        initializeText(); // 텍스트 초기화
        
        // 버튼의 border 스타일 업데이트
        lvButtons.forEach(btn => btn.style.border = "none"); // 모든 버튼 border 제거
        e.target.style.border = "2.5px solid #FFD700"; // 선택된 버튼에 border 추가
    });
});



// 텍스트 선택 및 복사 방지를 위한 이벤트 리스너 추가
textToType.addEventListener('copy', (e) => {
    e.preventDefault();
    return false;
});

textToType.addEventListener('selectstart', (e) => {
    e.preventDefault();
    return false;
});

textToType.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    return false;
});

// 키보드 단축키로 복사하는 것을 방지
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        if (e.key === 'c' || e.key === 'C' || e.key === 'v' || e.key === 'V') {
            e.preventDefault();
            return false;
        }
    }
});


// 초기화
initializeText();
loadHighScore();