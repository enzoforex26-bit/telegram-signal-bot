from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "7070480242:AAH7OgGyg7RA3Q_gog0LEQ43WqNQQo2sUew"
CHAT_ID = -1002031929245  

@app.route('/send', methods=['POST'])
def send_signal():
    data = request.json

    pair = data.get("pair")
    entry = float(data.get("entry"))
    sl = round(entry - 5, 2)
    tp = round(entry + 15, 2)

    message = f"""🚨 <b>BUY {pair}</b>
Entry: {entry}
SL: {sl}
TP: {tp}
#SwissGoldTrades"""

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    r = requests.post(telegram_url, data=payload)
    return r.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
