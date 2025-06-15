let codeMirrorEditor;
const runBtn = document.getElementById("run-code");
const customInput = document.getElementById("custom-input");
const customOutput = document.getElementById("custom-output");

runBtn.addEventListener("click", async () => {
  const code = codeMirrorEditor.getValue().trim();
  const testInput = customInput.value;

  if (!code) {
    alert("코드를 입력해 주세요!");
    return;
  }

  customOutput.textContent = "⏳ 실행 중...";

  try {
    const res = await fetch("/run_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, input: testInput })
    });

    const data = await res.json();
    customOutput.textContent = data.output || "(출력 없음)";
  } catch (err) {
    customOutput.textContent = "🚨 실행 중 오류 발생";
    console.error(err);
  }
});


document.addEventListener("DOMContentLoaded", async () => {
  const problemTitle = document.getElementById("problem-title");
  const problemDescription = document.getElementById("problem-description");
  const inputExample = document.getElementById("input-example");
  const outputExample = document.getElementById("output-example");
  const submitBtn = document.getElementById("submit-code");
  const resultOutput = document.getElementById("result-output");
  const judgeStatus = document.getElementById("judge-status");

  // ✅ CodeMirror 에디터 초기화
  codeMirrorEditor = CodeMirror.fromTextArea(document.getElementById("code-input"), {
    mode: "python",
    theme: "material-darker",
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    keyMap: "sublime",     
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    extraKeys: {
      Tab: function(cm) {
        cm.replaceSelection("    ", "end");
      }
    }
  });



  // 문제 불러오기
  async function loadProblem() {
    try {
      const res = await fetch("/get_problem");
      const data = await res.json();

      problemTitle.textContent = data.title;
      problemDescription.textContent = data.description;
      inputExample.textContent = data.input;
      outputExample.textContent = data.output;
    } catch (err) {
      problemTitle.textContent = "문제를 불러오지 못했습니다.";
      console.error(err);
    }
  }

  // 코드 제출 및 채점 요청
  submitBtn.addEventListener("click", async () => {
    const code = codeMirrorEditor.getValue().trim();
    if (!code) {
      alert("코드를 입력해 주세요!");
      return;
    }

    judgeStatus.textContent = "채점 중...";
    judgeStatus.style.display = "inline";

    try {
      const res = await fetch("/submit_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code })
      });

      const data = await res.json();
      judgeStatus.textContent = "채점 완료!";
      resultOutput.textContent = data.result || "결과 없음";
    } catch (err) {
      judgeStatus.textContent = "채점 실패";
      resultOutput.textContent = "서버 오류가 발생했습니다.";
      console.error(err);
    }
  });

  // 첫 진입 시 문제 불러오기
  await loadProblem();
});
