async function updateBot() {
    try {
        const res = await fetch('/api/signal');
        const data = await res.json();

        const statusEl = document.getElementById("status");
        const signalEl = document.getElementById("signal");
        const confEl = document.getElementById("confidence");

        signalEl.innerText = data.prediction;
        confEl.innerText = `Confiança: ${data.confidence}%`;
        
        if(data.prediction.includes("AZUL")) {
            signalEl.style.color = "#007bff";
            statusEl.innerText = "⚠️ PROTEJA NO EMPATE (TIE)";
        } else if(data.prediction.includes("VERMELHO")) {
            signalEl.style.color = "#ff4b4b";
            statusEl.innerText = "⚠️ PROTEJA NO EMPATE (TIE)";
        } else {
            signalEl.style.color = "#fff";
            statusEl.innerText = "ANONYMOUS BOT ANALISANDO...";
        }

        // Atualiza histórico visual
        const histEl = document.getElementById("history");
        histEl.innerHTML = data.history.map(r => 
            `<span class="dot ${r}">${r}</span>`
        ).join("");

    } catch (e) { console.log("Erro de conexão."); }
}
setInterval(updateBot, 3000);
