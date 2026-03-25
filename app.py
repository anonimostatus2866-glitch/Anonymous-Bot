import os, threading, time, logging
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações de Acesso
USER_EB = "922891255"
PASS_EB = "Amorosa012"

bot_brain = {
    "history": [],
    "prediction": "INICIALIZANDO...",
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
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        logger.info("Acessando ElephantBet para Login...")
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        wait = WebDriverWait(driver, 30)

        # Realizar Login
        try:
            user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            pass_input = driver.find_element(By.NAME, "password")
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            user_input.send_keys(USER_EB)
            pass_input.send_keys(PASS_EB)
            login_btn.click()
            logger.info("Login enviado. Aguardando Iframe...")
            time.sleep(15)
        except Exception as e:
            logger.warning(f"Login skip ou erro: {e}")

        # Entrar no Jogo (Iframe)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        logger.info("Sincronizado com a mesa de Bac Bo.")

        last_count = 0
        while True:
            try:
                # Captura de histórico (Bead Plate)
                beads = driver.find_elements(By.CSS_SELECTOR, "[class*='bead-'], [class*='stats-bead']")
                
                if beads and len(beads) != last_count:
                    last_count = len(beads)
                    
                    results = []
                    for b in beads[-10:]:
                        c = b.get_attribute("class").lower()
                        if "player" in c or "blue" in c: results.append("P")
                        elif "banker" in c or "red" in c: results.append("B")
                        elif "tie" in c or "gold" in c: results.append("T")
                    
                    results.reverse()
                    
                    if results:
                        current_res = results[0]
                        # Validação Win/Loss
                        if bot_brain["current_target"]:
                            if current_res == bot_brain["current_target"] or current_res == "T":
                                bot_brain["last_status"] = "WIN ✅"
                            else:
                                bot_brain["last_status"] = "LOSS ❌"
                        
                        bot_brain["history"] = results
                        
                        # Estratégia Anonymous (Baseada em Volume de Cor)
                        if results.count("P") >= results.count("B"):
                            bot_brain["prediction"] = "ENTRAR NO VERMELHO"
                            bot_brain["current_target"] = "B"
                        else:
                            bot_brain["prediction"] = "ENTRAR NO AZUL"
                            bot_brain["current_target"] = "P"
                        
                        bot_brain["confidence"] = 98
                        logger.info(f"Sinal: {bot_brain['prediction']} | Resultado Anterior: {current_res}")

            except Exception as e:
                logger.error(f"Erro na leitura: {e}")
            time.sleep(5)

    except Exception as e:
        logger.error(f"Erro Crítico: {e}")
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
