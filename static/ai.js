async function updateBot() {
    try {
        const res = await fetch('/api/signal');
        const data = await res.json();

        if (data.history.length > 0) {
            document.getElementById("signal").innerText = data.prediction;
            document.getElementById("confidence").innerText = `Confiança: ${data.confidence}%`;
            
            const signalEl = document.getElementById("signal");
            if(data.prediction.includes("AZUL")) signalEl.style.color = "#007bff";
            else if(data.prediction.includes("VERMELHO")) signalEl.style.color = "#ff4b4b";

            const histEl = document.getElementById("history");
            histEl.innerHTML = data.history.map(r => 
                `<span class="dot ${r}">${r}</span>`
            ).join("");
            
            document.getElementById("status").innerText = "SINALIZADOR ATIVO (PROTEJA TIE)";
        }
    } catch (e) { console.error("Erro na API"); }
}
setInterval(updateBot, 3000);
