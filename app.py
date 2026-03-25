import random
import time
import threading
from flask import Flask, jsonify, render_template

app = Flask(__name__)

system = {
    "status": "waiting",
    "signal": None,
    "confidence": 0,
    "result": None,
    "history": []
}

def generate_signal():
    base = random.random()

    if base < 0.5:
        value = round(random.uniform(1.20, 1.80), 2)
        confidence = random.randint(60, 75)
    elif base < 0.8:
        value = round(random.uniform(2.00, 3.50), 2)
        confidence = random.randint(70, 85)
    else:
        value = round(random.uniform(4.00, 8.00), 2)
        confidence = random.randint(80, 95)

    return value, confidence

def generate_real_result():
    base = random.random()

    if base < 0.5:
        return round(random.uniform(1.00, 2.00), 2)
    elif base < 0.8:
        return round(random.uniform(2.00, 4.00), 2)
    else:
        return round(random.uniform(4.00, 10.00), 2)

def cycle():
    global system

    while True:
        # WAIT PHASE
        system["status"] = "waiting"
        system["signal"] = None
        system["result"] = None
        time.sleep(8)

        # GENERATE SIGNAL
        value, confidence = generate_signal()
        system["signal"] = f"{value}x"
        system["confidence"] = confidence
        system["status"] = "signal"

        time.sleep(6)

        # RESULT
        real = generate_real_result()
        system["result"] = f"{real}x"

        if real >= value:
            outcome = "WIN"
        else:
            outcome = "LOSS"

        system["history"].insert(0, {
            "signal": system["signal"],
            "result": system["result"],
            "outcome": outcome
        })

        if len(system["history"]) > 10:
            system["history"].pop()

        system["status"] = outcome

        time.sleep(5)

threading.Thread(target=cycle, daemon=True).start()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/data")
def data():
    return jsonify(system)

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
