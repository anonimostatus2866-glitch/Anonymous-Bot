async function updateBot() {
    try {
        const res = await fetch('/api/signal');
        const data = await res.json();

        const signalEl = document.getElementById("signal");
        const statusEl = document.getElementById("status");
        const histEl = document.getElementById("history");

        if (data.history.length > 0) {
            signalEl.innerText = data.prediction;
            signalEl.style.color = data.prediction.includes("VERMELHO") ? "#ff4b4b" : "#007bff";
            
            statusEl.innerText = data.last_status === "WAITING" ? "ANALISANDO PRÓXIMA RODADA..." : data.last_status;
            statusEl.style.color = data.last_status.includes("WIN") ? "#00ff41" : "#ff4b4b";

            document.getElementById("confidence").innerText = `Confiança: ${data.confidence}%`;

            histEl.innerHTML = data.history.map(r => 
                `<span class="dot ${r}">${r}</span>`
            ).join("");
        }
    } catch (e) { console.log("Erro de conexão."); }
}
setInterval(updateBot, 3000);
