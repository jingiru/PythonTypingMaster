// DOM 요소 가져오기
const textToType = document.getElementById("text-to-type");
const typingInput = document.getElementById("typing-input");
const speedDisplay = document.getElementById("speed");
const accuracyDisplay = document.getElementById("accuracy");
const submitButton = document.getElementById("submit-button"); // 제출 버튼

// 타이핑 연습 텍스트
const typingTexts = [
  'print',
  'for',
  'if',
  'print(5)',
  'print("hello")',
  'if x > 0:',
  'input'
];

// 소리 재생 함수
function playSound(type) {
  const audio = new Audio(type === "correct" ? "/static/correct.mp3" : "/static/incorrect.mp3");
  audio.play();
}

// 초기 상태 변수
let currentText = "";
let startTime = null;
let correctChars = 0;

// 연습 텍스트 초기화
function initializeText() {
  const randomIndex = Math.floor(Math.random() * typingTexts.length);
  currentText = typingTexts[randomIndex];
  textToType.textContent = currentText;
  typingInput.value = "";
  startTime = null;
  correctChars = 0;
  updateStats(0, 0); // 초기 속도 및 정확도 0으로 설정
}

// 통계 업데이트 함수
function updateStats(speed, accuracy) {
  speedDisplay.textContent = speed; // CPM 표시
  accuracyDisplay.textContent = accuracy; // 정확도 표시
}

// 정확도와 속도 계산
function calculateStats(userInput) {
  const sanitizedUserInput = userInput.replace(/\s+/g, "");
  const sanitizedCurrentText = currentText.replace(/\s+/g, "");

  let correctCount = 0;
  for (let i = 0; i < sanitizedUserInput.length; i++) {
    if (sanitizedUserInput[i] === sanitizedCurrentText[i]) {
      correctCount++;
    }
  }

  const elapsedTime = (new Date() - startTime) / 1000 / 60; // 분 단위
  const speed = Math.round(correctCount / elapsedTime) || 0;
  const accuracy = Math.round((correctCount / sanitizedCurrentText.length) * 100) || 0;

  updateStats(speed, accuracy);
  return { speed, accuracy };
}

// 정답 처리
function handleCorrect() {
  playSound("correct"); // 정답 소리 재생
  typingInput.style.borderColor = "#4CAF50";
  setTimeout(() => {
    initializeText(); // 새 텍스트로 초기화
    typingInput.focus();
  }, 500); // 0.5초 후 이동
}

// 오답 처리
function handleIncorrect() {
  playSound("incorrect"); // 경고 소리 재생
  typingInput.value = ""; // 입력창 초기화
  typingInput.style.borderColor = "#FF4C4C"; // 빨간색 테두리 표시
}

// Enter 키 입력 처리
typingInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter") {
    const userInput = typingInput.value;

    // 정확도 계산
    const { accuracy } = calculateStats(userInput);

    if (accuracy === 100) {
      handleCorrect();
    } else {
      handleIncorrect();
    }

    event.preventDefault(); // Enter 키 기본 동작 방지
  }
});

// 제출 버튼 클릭 처리
submitButton.addEventListener("click", () => {
  const userInput = typingInput.value;

  // 정확도 계산
  const { accuracy } = calculateStats(userInput);

  if (accuracy === 100) {
    handleCorrect();
  } else {
    handleIncorrect();
  }
});

// 입력 이벤트 처리
typingInput.addEventListener("input", () => {
  if (!startTime) startTime = new Date();

  const userInput = typingInput.value;
  const { accuracy } = calculateStats(userInput);

  if (accuracy === 100) {
    handleCorrect();
  }
});

// 초기화
initializeText();
