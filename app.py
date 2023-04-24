from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

def translate(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=("번역: 영어를 한국어로 번역합니다. 만약 한국어이라면 영어로 번역합니다\n"
                "입력: 문장\n"
                "번역: 문장이 영어면 한국어로 번역하고 문장이 한국어면 영어로 번역한 문장입니다.  \n\n"
                f"입력: {text}\n"
                "번역: "),
        temperature=0.5,
        max_tokens=1024,
        n=1,
        stop=None,
        timeout=60,
    )

    translation = response.choices[0].text.strip()
    return translation

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate_text():
    text = request.form["text"]
    translation = translate(text)
    return render_template("index.html", translation=translation)

if __name__ == "__main__":
    app.run(debug=True)