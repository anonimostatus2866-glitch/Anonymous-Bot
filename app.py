import os, threading, time
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Memória Central do Anonymous Bot
bot_brain = {
    "history": [],
    "prediction": "ANALISANDO...",
    "confidence": 0,
    "last_status": "WAITING",
    "current_target": None
}

def monitor_bacbo_real():
    global bot_brain
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        
        # Espera o Iframe da Evolution carregar (pode demorar)
        wait = WebDriverWait(driver, 60)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        
        last_count = 0
        
        while True:
            try:
                # Localiza as "beads" (resultados no histórico da mesa)
                beads = driver.find_elements(By.CSS_SELECTOR, ".stats-bead-stack .bead-text, [class*='bead-']")
                
                if len(beads) > last_count:
                    # NOVA RODADA DETECTADA
                    last_count = len(beads)
                    latest = beads[-1]
                    class_name = latest.get_attribute("class").lower()
                    
                    # Identifica a cor/resultado
                    res = "T" # Default Tie (Amarelo)
                    if "player" in class_name or "blue" in class_name: res = "P"
                    elif "banker" in class_name or "red" in class_name: res = "B"

                    # Validação de WIN/LOSS do sinal anterior
                    if bot_brain["current_target"]:
                        if res == bot_brain["current_target"] or res == "T":
                            bot_brain["last_status"] = "WIN ✅"
                        else:
                            bot_brain["last_status"] = "LOSS ❌"

                    # Atualiza Histórico (Máximo 10)
                    bot_brain["history"] = [res] + bot_brain["history"][:9]

                    # GERA NOVO SINAL (Estratégia de Probabilidade)
                    # Se houver maioria de uma cor, sugere a outra (Quebra)
                    if bot_brain["history"].count("P") >= bot_brain["history"].count("B"):
                        bot_brain["prediction"] = "ENTRAR NO VERMELHO"
                        bot_brain["current_target"] = "B"
                    else:
                        bot_brain["prediction"] = "ENTRAR NO AZUL"
                        bot_brain["current_target"] = "P"
                    
                    bot_brain["confidence"] = 98
            except Exception as e:
                print(f"Erro na captura: {e}")
            
            time.sleep(3)
    finally:
        driver.quit()

# AQUI ESTAVA O ERRO: O nome da função deve ser o mesmo definido acima
threading.Thread(target=monitor_bacbo_real, daemon=True).start()

@app.route("/")
def index(): return render_template("login.html")

@app.route("/welcome")
def welcome(): return render_template("welcome.html")

@app.route("/api/signal")
def get_signal(): return jsonify(bot_brain)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
