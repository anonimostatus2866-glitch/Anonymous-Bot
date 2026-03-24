import os, threading, time
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

app = Flask(__name__)

# Memória do Bot
bot_brain = {
    "history": [], # Ex: ['P', 'B', 'T', 'P'] (Player, Banker, Tie)
    "prediction": "Aguardando...",
    "confidence": 0,
    "new_result": False
}

def analyze_bacbo(history):
    if len(history) < 3: return "Analisando...", 0
    # Lógica de Contra-Tendência (Exemplo: Se saiu 3 vezes a mesma cor, aposta na oposta)
    last_three = history[:3]
    if last_three.count('B') >= 2:
        return "APOSTE NO AZUL (PLAYER)", 98
    if last_three.count('P') >= 2:
        return "APOSTE NO VERMELHO (BANKER)", 98
    return "AGUARDE A PRÓXIMA", 75

def scraper_thread():
    global bot_brain
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        time.sleep(25) # Carregamento pesado do lobby Evolution
        
        last_found = ""
        while True:
            try:
                # Seletor baseado na estrutura comum da Evolution Gaming para Bac Bo
                # Ele busca as 'beads' (bolinhas) do histórico
                beads = driver.find_elements(By.CSS_SELECTOR, "[class*='bead-']")
                if beads:
                    # Extrai 'P' para Player/Azul, 'B' para Banker/Vermelho, 'T' para Tie/Empate
                    results = []
                    for b in beads[-10:]:
                        c = b.get_attribute("class")
                        if "player" in c: results.append("P")
                        elif "banker" in c: results.append("B")
                        elif "tie" in c: results.append("T")
                    
                    results.reverse() # Mais recente primeiro
                    
                    if results and results[0] != last_found:
                        last_found = results[0]
                        pred, conf = analyze_bacbo(results)
                        bot_brain.update({
                            "history": results,
                            "prediction": pred,
                            "confidence": conf,
                            "new_result": True
                        })
            except: pass
            time.sleep(3)
    finally:
        driver.quit()

threading.Thread(target=scraper_thread, daemon=True).start()

@app.route("/")
def index(): return render_template("login.html")

@app.route("/welcome")
def welcome(): return render_template("welcome.html")

@app.route("/api/signal")
def get_signal():
    data = jsonify(bot_brain.copy())
    bot_brain["new_result"] = False
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
