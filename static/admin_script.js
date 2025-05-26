let refreshInterval = null;

// 상태 기억: localStorage에서 isRealTime 값 불러오기
let isRealTime = localStorage.getItem("isRealTime") === "true";

const toggleBtn = document.getElementById("toggle-refresh-btn");

// 자동 새로고침 시작
function startAutoRefresh(intervalSec) {
  stopAutoRefresh();
  refreshInterval = setInterval(() => {
    location.reload();
  }, intervalSec * 1000);
}

// 자동 새로고침 정지
function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

// 버튼 UI 업데이트 함수
function updateToggleButtonUI() {
  if (isRealTime) {
    toggleBtn.textContent = "실시간 보기 ON";
    toggleBtn.style.backgroundColor = "#FFD700";
    toggleBtn.style.color = "black";
    startAutoRefresh(1);
  } else {
    toggleBtn.textContent = "실시간 보기 OFF";
    toggleBtn.style.backgroundColor = "gray";
    toggleBtn.style.color = "white";
    startAutoRefresh(100);
  }
}

// 버튼 클릭 이벤트
toggleBtn.addEventListener("click", () => {
  isRealTime = !isRealTime;
  localStorage.setItem("isRealTime", isRealTime); // 상태 저장
  updateToggleButtonUI();
});

// 최초 로딩 시 UI 초기화 및 리프레시 시작
updateToggleButtonUI();


// --- 기존 기능 그대로 유지 ---

function presetIds() {
  const startId = document.getElementById('start-id').value.trim();
  const endId = document.getElementById('end-id').value.trim();

  if (!startId || !endId) {
    alert("시작 학번과 종료 학번을 입력하세요.");
    return;
  }

  fetch("/preset_ids", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start_id: startId, end_id: endId })
  }).then(res => {
    if (res.ok) location.reload();
  });
}

function clearAll() {
  if (!confirm("정말 전체를 초기화하시겠습니까?")) return;

  fetch("/clear_all", {
    method: "POST"
  }).then(res => {
    if (res.ok) location.reload();
  });
}

document.getElementById("start-exam-btn").addEventListener("click", () => {
  const durationInput = parseFloat(document.getElementById("exam-duration").value);

  if (isNaN(durationInput) || durationInput <= 0) {
    alert("시험 시간을 0.5분(30초) 이상 입력해 주세요.");
    return;
  }

  const minutes = Math.floor(durationInput);
  const seconds = (durationInput % 1) === 0.5 ? 30 : 0;
  const totalSeconds = minutes * 60 + seconds;

  fetch("/start_exam", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration: totalSeconds })
  }).then(res => {
    if (res.ok) {
      alert(`시험이 시작되었습니다! (${minutes}분 ${seconds}초)`);
    } else {
      alert("시험 시작 실패!");
    }
  });
});