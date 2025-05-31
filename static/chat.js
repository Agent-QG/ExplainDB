function sendMessage() {
    const input = document.getElementById("user-input");
    const question = input.value;
    const db = document.getElementById("db-select").value;

    if (!question.trim()) return;

    appendMessage("user", question);
    input.value = "";

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, database: db })
    })
    .then(response => response.json())
.then(data => {
    appendMessage("bot", data.final_answer);

    if (data.main_chart && data.main_explanation) {
        appendImage(data.main_chart);
        appendMessage("bot", `<strong>Explanation:</strong> ${data.main_explanation}`);
    }

    if (data.recommendations.length > 0) {
        appendMessage("bot", "<strong>You may be interested in：</strong>");
        data.recommendations.forEach(item => {
            appendMessage("bot", `<strong>Goal:</strong> ${item.goal}`);
            appendImage(item.chart);
            appendMessage("bot", `<strong>Explanation:</strong> ${item.explanation}`);
        });
    }
});

}

function appendMessage(sender, text) {
    const box = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerHTML = text;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}

function appendImage(base64) {
    const box = document.getElementById("chat-box");
    const img = document.createElement("img");
    img.src = "data:image/png;base64," + base64;
    box.appendChild(img);
    box.scrollTop = box.scrollHeight;
}
