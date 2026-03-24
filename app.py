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
    "history": [],
    "prediction": "ANALISANDO...",
    "confidence": 0,
    "new_result": False
}

def monitor_bacbo():
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
        
        # Espera o Iframe do jogo carregar
        wait = WebDriverWait(driver, 40)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        
        last_found = ""
        while True:
            try:
                # Seletor focado na classe de histórico da Evolution
                beads = driver.find_elements(By.CSS_SELECTOR, ".stats-bead-stack .bead-text")
                if not beads:
                    # Alternativa se o primeiro falhar
                    beads = driver.find_elements(By.CSS_SELECTOR, "[class*='bead-']")

                if beads:
                    results = []
                    # Pega os últimos 12 resultados
                    for b in beads[-12:]:
                        txt = b.text.upper() if b.text else ""
                        if not txt:
                            c = b.get_attribute("class").lower()
                            if "player" in c: txt = "P"
                            elif "banker" in c: txt = "B"
                            elif "tie" in c: txt = "T"
                        
                        if txt in ['P', 'B', 'T']:
                            results.append(txt)
                    
                    results.reverse()

                    if results and results[0] != last_found:
                        last_found = results[0]
                        # IA: Estratégia de repetição (Padrão de Quebra)
                        if results.count('P') > results.count('B'):
                            pred, conf = "ENTRAR NO VERMELHO (BANKER)", 98
                        else:
                            pred, conf = "ENTRAR NO AZUL (PLAYER)", 98
                        
                        bot_brain.update({
                            "history": results,
                            "prediction": pred,
                            "confidence": conf,
                            "new_result": True
                        })
            except Exception as e:
                print(f"Erro na leitura: {e}")
            
            time.sleep(4)
    finally:
        driver.quit()

threading.Thread(target=monitor_bacbo, daemon=True).start()

@app.route("/")
def index(): return render_template("login.html")

@app.route("/welcome")
def welcome(): return render_template("welcome.html")

@app.route("/api/signal")
def get_signal():
    return jsonify(bot_brain)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
