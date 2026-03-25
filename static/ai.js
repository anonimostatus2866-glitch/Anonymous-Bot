async function updateBot() {
    try {
        const response = await fetch('/api/signal');
        const data = await response.json();

        const statusEl = document.getElementById("status");
        const signalEl = document.getElementById("signal");
        const confEl = document.getElementById("confidence");
        const histEl = document.getElementById("history");

        // Atualiza Status de Win/Loss
        if (data.last_status !== "WAITING") {
            statusEl.innerText = data.last_status;
            statusEl.className = data.last_status.includes("WIN") ? "status-bar win" : "status-bar loss";
        }

        // Atualiza o Sinal Atual
        signalEl.innerText = data.prediction;
        if (data.prediction.includes("VERMELHO")) signalEl.style.color = "#ff4b4b";
        else if (data.prediction.includes("AZUL")) signalEl.style.color = "#007bff";

        confEl.innerText = `Confiança: ${data.confidence}%`;

        // Renderiza as bolinhas do histórico real
        if (data.history.length > 0) {
            histEl.innerHTML = data.history.map(r => 
                `<span class="dot ${r}">${r}</span>`
            ).join("");
        }

    } catch (e) {
        console.log("Aguardando conexão com o servidor...");
    }
}

// Inicia o loop
setInterval(updateBot, 2000);
