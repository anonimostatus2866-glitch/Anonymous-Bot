async function updateBot() {
    const res = await fetch('/api/signal');
    const data = await res.json();

    const signalEl = document.getElementById("signal");
    const statusEl = document.getElementById("status");
    const histEl = document.getElementById("history");

    if (data.error_log) {
        statusEl.innerText = "ERRO DE CONEXÃO: " + data.error_log.substring(0, 20);
        return;
    }

    if (data.history.length > 0) {
        signalEl.innerText = data.prediction;
        signalEl.style.color = data.prediction.includes("VERMELHO") ? "#ff4b4b" : "#007bff";
        statusEl.innerText = data.last_status;
        statusEl.style.color = data.last_status.includes("WIN") ? "#00ff41" : "#ff4b4b";
        document.getElementById("confidence").innerText = `Probabilidade: ${data.confidence}%`;
        histEl.innerHTML = data.history.map(r => `<span class="dot ${r}">${r}</span>`).join("");
    }
}
setInterval(updateBot, 3000);
