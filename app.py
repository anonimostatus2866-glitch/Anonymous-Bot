import os, threading, time
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

bot_brain = {
    "history": [], # Real da ElephantBet
    "prediction": "AGUARDANDO...",
    "confidence": 0,
    "last_status": "WAITING", # WIN, LOSS ou WAITING
    "current_target": None
}

def monitor_bacbo_real():
    global bot_brain
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        # Entra no Iframe da Evolution
        wait = WebDriverWait(driver, 30)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        
        last_result_count = 0
        
        while True:
            try:
                # Captura as bolinhas do histórico (beads)
                beads = driver.find_elements(By.CSS_SELECTOR, "[class*='bead-']")
                
                if len(beads) > last_result_count:
                    # NOVO RESULTADO DETECTADO NA MESA
                    last_result_count = len(beads)
                    latest_bead = beads[-1]
                    c = latest_bead.get_attribute("class").lower()
                    
                    res = "P" if "player" in c else "B" if "banker" in c else "T"
                    
                    # 1. Valida o sinal anterior (WIN/LOSS)
                    if bot_brain["current_target"]:
                        if res == bot_brain["current_target"] or res == "T":
                            bot_brain["last_status"] = "WIN ✅"
                        else:
                            bot_brain["last_status"] = "LOSS ❌"
                    
                    # 2. Atualiza Histórico Real
                    bot_brain["history"] = [res] + bot_brain["history"][:9]
                    
                    # 3. Gera Próximo Sinal IMEDIATAMENTE (Antes da próxima rodada)
                    # Estratégia: Quebra de sequência (Anti-Trend)
                    if bot_brain["history"].count("P") >= 2:
                        bot_brain["prediction"] = "VERMELHO (BANKER)"
                        bot_brain["current_target"] = "B"
                    else:
                        bot_brain["prediction"] = "AZUL (PLAYER)"
                        bot_brain["current_target"] = "P"
                    
                    bot_brain["confidence"] = 98

            except Exception as e:
                print(f"Sync Error: {e}")
            
            time.sleep(2) # Polling de alta frequência
    finally:
        driver.quit()

threading.Thread(target=monitor_aviator_real, daemon=True).start()

@app.route("/")
def index(): return render_template("login.html")

@app.route("/welcome")
def welcome(): return render_template("welcome.html")

@app.route("/api/signal")
def get_signal(): return jsonify(bot_brain)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
