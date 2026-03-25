import os, threading, time, logging
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

USER_EB, PASS_EB = "922891255", "Amorosa012"

bot_brain = {
    "history": [],
    "prediction": "RITUAL DE ACESSO...",
    "last_status": "LIMPANDO ERROS",
    "current_target": None
}

def monitor_bacbo_real():
    global bot_brain
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
    try:
        # 1. Login Inicial (Garante Sessão)
        driver.get("https://www.elephantbet.co.ao/pt/auth/login")
        wait = WebDriverWait(driver, 25)
        
        u = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        u.send_keys(USER_EB)
        driver.find_element(By.NAME, "password").send_keys(PASS_EB)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(8)

        # 2. Abre a mesa "Inativa"
        driver.get("https://www.elephantbet.co.ao/pt/casino/game-view/420032042/bac-bo-ao-vivo")
        
        # 3. Entra no Iframe para lidar com o erro interno
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        # 4. TRATAMENTO DO ERRO: Clica no OK do modal de mesa inativa
        try:
            # Procura botões com texto "OK", "Confirmar" ou ícones de fechar (X)
            btn_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'OK') or contains(., 'Confirmar') or contains(., 'Fechar')]")))
            btn_ok.click()
            logging.info("Pop-up de mesa inativa fechado.")
            time.sleep(5)
        except:
            logging.info("Nenhum pop-up detectado, prosseguindo...")

        # 5. Localiza e Clica no "Bac Bo Brasileiro" no menu lateral ou grid
        # Usamos texto parcial para capturar qualquer variação
        btn_brasil = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Brasileiro') or contains(text(), 'Brasil')]")))
        btn_brasil.click()
        logging.info("Mesa Brasileira selecionada.")
        time.sleep(10)

        # 6. Loop de Monitoramento (Agora na mesa certa)
        while True:
            # Script para pegar as classes das bolinhas (Beads)
            script = "return Array.from(document.querySelectorAll('[class*=\"bead-\"]')).map(el => el.className).slice(-10);"
            classes = driver.execute_script(script)
            
            if classes:
                res_map = {'player': 'P', 'banker': 'B', 'tie': 'T'}
                translated = []
                for c in classes:
                    c_low = c.lower()
                    found = next((v for k, v in res_map.items() if k in c_low), 'T')
                    translated.append(found)
                
                bot_brain["history"] = translated[::-1]
                bot_brain["last_status"] = "OPERANDO 100% ✅"
                
                # Estratégia: Inversão de Tendência
                p_count = translated.count('P')
                b_count = translated.count('B')
                bot_brain["current_target"] = 'B' if p_count >= b_count else 'P'
                bot_brain["prediction"] = f"ENTRAR NO {'VERMELHO' if bot_brain['current_target']=='B' else 'AZUL'}"

            time.sleep(5)

    except Exception as e:
        logging.error(f"Erro no Ritual: {e}")
        bot_brain["last_status"] = "REINICIANDO ACESSO..."
    finally:
        driver.quit()
        time.sleep(5)
        monitor_bacbo_real()

threading.Thread(target=monitor_bacbo_real, daemon=True).start()

@app.route("/api/signal")
def get_signal(): return jsonify(bot_brain)
