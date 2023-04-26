from flask import Flask, render_template, request, send_from_directory
import openai
import os
from PyPDF2 import PdfReader, PdfWriter, PdfFileMerger
from reportlab.pdfgen import canvas
from io import BytesIO
import base64

app = Flask(__name__)

# OpenAI API 인증 정보 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")


if not os.path.exists('temp'):
    os.makedirs('temp')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form.get('text')
    target_language = request.form['target_language']
    pdf_file = request.files.get('pdf-upload')
    
    if text:
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

    elif pdf_file:
        # Read the PDF
        reader = PdfReader(pdf_file.stream)
        merger = PdfFileMerger()

        # Translate each page and add it to the output PDF
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
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

            # Create a new PDF page with the translated text
            packet = BytesIO()
            c = canvas.Canvas(packet)
            c.setFont("Helvetica", 12)
            c.drawString(10, 800, translated_text)
            c.save()

            # Move to the beginning of the StringIO buffer
            packet.seek(0)

            # Merge the new page with the output PDF
            new_page = PdfReader(packet)
            merger.merge(i, new_page)

        # Save the output PDF to a temporary file
        output_pdf_filename = f"translated_pdf_{base64.urlsafe_b64encode(os.urandom(6)).decode('utf-8')}.pdf"
        output_pdf_path = os.path.join('temp', output_pdf_filename)
        with open(output_pdf_path, 'wb') as output_pdf_file:
            merger.write(output_pdf_file)

        return {'translated_pdf_filename': output_pdf_filename}

    else:
        return {'error': 'No text or PDF provided'}

@app.route('/temp/<path:filename>')
def download(filename):
    try:
        return send_from_directory('temp', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
