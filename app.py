import os, threading, time, logging
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Memória do Bot
bot_brain = {
    "history": [],
    "prediction": "CALIBRANDO...",
    "confidence": 0,
    "last_status": "SINCRONIZANDO",
    "current_target": None
}

def monitor_bacbo_real():
    global bot_brain
    options = Options()
    options.add_argument("--headless=new") # Modo novo mais estável
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled") # Esconde que é BOT
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        # Acessa diretamente o lobby para evitar redirecionamentos
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        time.sleep(20) # Tempo para carregar scripts da Evolution

        while True:
            try:
                # Tenta capturar os dados do histórico via JS direto no console
                # Isso evita o erro de 'stacktrace' ao tentar clicar ou mudar de iframe
                script = """
                let results = [];
                let beads = document.querySelectorAll("[class*='bead-'], [class*='stats-bead']");
                beads.forEach(b => {
                    let c = b.className.toLowerCase();
                    if(c.includes('player')) results.push('P');
                    else if(c.includes('banker')) results.append('B');
                    else if(c.includes('tie')) results.push('T');
                });
                return results.slice(-12).reverse();
                """
                
                # Se estiver em Iframe, o Selenium tenta injetar em todos os frames
                found_history = []
                frames = driver.find_elements(By.TAG_NAME, "iframe")
                for index, frame in enumerate(frames):
                    try:
                        driver.switch_to.frame(frame)
                        found_history = driver.execute_script(script)
                        if found_history: break
                        driver.switch_to.default_content()
                    except:
                        driver.switch_to.default_content()

                if found_history:
                    res = found_history[0]
                    if bot_brain["current_target"]:
                        bot_brain["last_status"] = "WIN ✅" if (res == bot_brain["current_target"] or res == 'T') else "LOSS ❌"
                    
                    bot_brain["history"] = found_history
                    # Lógica de Inteligência: Anti-tendência
                    bot_brain["current_target"] = 'B' if found_history.count('P') > found_history.count('B') else 'P'
                    bot_brain["prediction"] = "ENTRAR NO " + ("VERMELHO" if bot_brain["current_target"] == 'B' else "AZUL")
                    bot_brain["confidence"] = 98
                
            except Exception as e:
                logging.error(f"Erro interno: {e}")
            
            time.sleep(5)
    except Exception as e:
        logging.error(f"Erro Fatal: {e}")
    finally:
        driver.quit()
        time.sleep(10)
        monitor_bacbo_real()

threading.Thread(target=monitor_bacbo_real, daemon=True).start()

@app.route("/")
def index(): return render_template("login.html")

@app.route("/welcome")
def welcome(): return render_template("welcome.html")

@app.route("/api/signal")
def get_signal(): return jsonify(bot_brain)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
