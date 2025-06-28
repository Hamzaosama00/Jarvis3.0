from flask import Flask, request, render_template, send_file
from flask_cors import CORS
import asyncio
import edge_tts
import requests
import re

app = Flask(__name__)
CORS(app)

# ✅ OpenRouter API Key and Model
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo-instruct"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("text", "")
    print(f"🧠 Asking AI: {user_input}")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are Jarvis, a helpful assistant."},
                    {"role": "user", "content": user_input}
                ]
            }
        )
        response_json = response.json()
        print("✅ AI Raw Reply:", response_json)

        if 'choices' in response_json and len(response_json['choices']) > 0:
            reply = response_json['choices'][0]['message']['content']
            # Clean markdown + emojis
            clean_reply = re.sub(r'[*_>`#\[\]\(\)]+', '', reply).strip()
            clean_reply = re.sub(r'[^\w\s,.?!\'\"@%$&:;<>-]', '', clean_reply)
            return {"response": clean_reply}
        else:
            return {"response": "❌ AI gave no response."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"response": f"❌ Error: {str(e)}"}, 500

@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    text = data.get("text", "")
    voice = data.get("voice", "en-US-GuyNeural")
    output_path = "output.mp3"

    try:
        asyncio.run(convert(text, voice, output_path))
        return send_file(output_path, mimetype="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}, 500

async def convert(text, voice, output_path):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_path)

if __name__ == "__main__":
    app.run(debug=False)
