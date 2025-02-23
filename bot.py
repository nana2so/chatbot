from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Remplace par tes infos Green API
INSTANCE_ID = "7105191613"  # Remplace avec ton ID d'instance Green API
API_TOKEN = "966e5893a594467fac2db0ba5c990940936e08c5d25e4532b9"  # Remplace avec ton Token API
API_URL = f"https://api.green-api.com/{INSTANCE_ID}/sendMessage/{API_TOKEN}"

# Stocke les sessions utilisateurs
user_sessions = {}

# Questions du chatbot
questions = [
    "Quel est le nom de l'entreprise ?",
    "Combien de personnes sont impliquées ?",
    "Quelle est la date et l'heure de début et de fin de la commande (YYYY-MM-DD HH:MM - HH:MM) ?",
    "Quel est le lieu de la commande de travail ?",
    "Quel est le nom du superviseur du site ?",
    "Quel est le numéro de téléphone du superviseur du site ?"
]

# Fonction pour envoyer un message WhatsApp via Green API
def send_message(chat_id, message):
    payload = {
        "chatId": chat_id,
        "message": message
    }
    headers = {"Content-Type": "application/json"}
    requests.post(API_URL, json=payload, headers=headers)

@app.route("/", methods=["GET"])
def home():
    return "Le chatbot fonctionne !"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    sender_id = data["senderData"]["chatId"]
    message = data["messageData"]["textMessageData"]["textMessage"]

    if sender_id not in user_sessions:
        user_sessions[sender_id] = {"step": 0, "answers": []}
        send_message(sender_id, questions[0])
    else:
        session = user_sessions[sender_id]
        step = session["step"]

        session["answers"].append(message)

        if step < len(questions) - 1:
            session["step"] += 1
            send_message(sender_id, questions[step + 1])
        else:
            final_response = "\n".join(f"{questions[i]} {session['answers'][i]}" for i in range(len(questions)))
            send_message(sender_id, f"Merci ! Voici votre demande :\n{final_response}")
            del user_sessions[sender_id]

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)