from flask import Flask, render_template, request
import openai_secret_manager
import openai
import os

app = Flask(__name__)

# OpenAI API 인증 정보 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data['text']
    target_language = data['target_language']
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(f"Translate the following text into {target_language}: {text}\n"
                f"Translation:"),
        temperature=0.5,
        max_tokens=1024,
        n = 1,
        stop=None,
        timeout=30,
    )
    translated_text = response.choices[0].text.strip()
    return {'translated_text': translated_text}

if __name__ == '__main__':
    app.run(debug=True)