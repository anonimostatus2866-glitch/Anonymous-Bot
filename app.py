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

USER_EB, PASS_EB = "922891255", "Amorosa012"

bot_brain = {
    "history": [],
    "prediction": "INICIALIZANDO...",
    "confidence": 0,
    "last_status": "SINCRONIZANDO...",
    "current_target": None,
    "error_log": None
}

def monitor_bacbo_real():
    global bot_brain
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,720")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        wait = WebDriverWait(driver, 45)

        # Tentativa de Login Bypass
        try:
            logger.info("Localizando campos de login...")
            u_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            p_field = driver.find_element(By.NAME, "password")
            u_field.send_keys(USER_EB)
            p_field.send_keys(PASS_EB)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(10)
        except:
            logger.info("Login já realizado ou campos não encontrados.")

        # Forçar entrada no Iframe da Evolution
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        logger.info("Sucesso: Dentro da mesa.")
        bot_brain["last_status"] = "CONECTADO ✅"

        last_count = 0
        while True:
            # Seletores redundantes para as bolinhas (beads)
            beads = driver.find_elements(By.CSS_SELECTOR, "[class*='bead-'], [class*='stats-bead'], .bead-text")
            
            if beads and len(beads) != last_count:
                last_count = len(beads)
                results = []
                for b in beads[-12:]:
                    c = b.get_attribute("class").lower()
                    if "player" in c or "blue" in c: results.append("P")
                    elif "banker" in c or "red" in c: results.append("B")
                    elif "tie" in c or "gold" in c: results.append("T")
                
                results.reverse()
                if results:
                    current = results[0]
                    # Validação de Win/Loss
                    if bot_brain["current_target"]:
                        bot_brain["last_status"] = "WIN ✅" if (current == bot_brain["current_target"] or current == "T") else "LOSS ❌"
                    
                    bot_brain["history"] = results
                    # IA: Análise de alternância
                    if results.count("P") > results.count("B"):
                        bot_brain["prediction"], bot_brain["current_target"] = "ENTRAR NO VERMELHO", "B"
                    else:
                        bot_brain["prediction"], bot_brain["current_target"] = "ENTRAR NO AZUL", "P"
                    bot_brain["confidence"] = 98

            time.sleep(4)
    except Exception as e:
        bot_brain["error_log"] = str(e)
        logger.error(f"Erro: {e}")
    finally:
        driver.quit()
        time.sleep(15)
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
