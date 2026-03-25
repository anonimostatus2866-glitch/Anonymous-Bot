async function updateUI() {
    try {
        const response = await fetch('/api/signal');
        const data = await response.json();

        const statusEl = document.getElementById("status");
        const signalEl = document.getElementById("signal");
        const histEl = document.getElementById("history");

        // Exibe o resultado da última rodada (Win/Loss)
        statusEl.innerText = data.last_status === "WAITING" ? "ANALISANDO PRÓXIMA RODADA..." : data.last_status;
        statusEl.style.color = data.last_status.includes("WIN") ? "#00ff41" : "#ff4b4b";

        // Exibe o sinal para a rodada ATUAL
        signalEl.innerText = data.prediction;
        signalEl.style.color = data.prediction.includes("AZUL") ? "#007bff" : "#ff4b4b";

        document.getElementById("confidence").innerText = `Probabilidade: ${data.confidence}%`;

        // Renderiza o histórico real da mesa
        histEl.innerHTML = data.history.map(r => 
            `<span class="dot ${r}">${r}</span>`
        ).join("");

    } catch (e) { console.error("Falha na sincronia."); }
}
setInterval(updateUI, 2000);
