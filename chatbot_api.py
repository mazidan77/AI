
# python --version
#  pip3 install flask
#   python -m pip install --upgrade google-generativeai
#    pip install flask google-generativeai flask-cors
#    pip install flask flask-cors google-generativeai pdfplumber python-docx
# python chatbot_api.py
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import pdfplumber
import docx
import io
import re
app = Flask(__name__)
CORS(app)




# Configure Gemini API
genai.configure(api_key="AIzaSyDS9tePm7YHqCSIVEzeuQ6DYX6XytbGQSg")
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat()

def extract_text_from_pdf(file_stream):
    text = ''
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

def extract_text_from_docx(file_stream):
    doc = docx.Document(file_stream)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text


@app.route('/chat', methods=['POST'])
def chat_with_bot():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    response = chat.send_message(user_message)
    return jsonify({'response': response.text})

@app.route('/analyze_cv', methods=['POST'])
def analyze_cv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read file content in-memory
    file_stream = io.BytesIO(file.read())

    # Extract text based on file extension
    if file.filename.lower().endswith('.pdf'):
        try:
            text = extract_text_from_pdf(file_stream)
        except Exception as e:
            return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
    elif file.filename.lower().endswith(('.docx', '.doc')):
        try:
            text = extract_text_from_docx(file_stream)
        except Exception as e:
            return jsonify({'error': f'Failed to process DOCX: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    if not text.strip():
        return jsonify({'error': 'Could not extract text from the CV'}), 400

    # Prepare prompt for Gemini AI to analyze the CV
    prompt = (
         "You are an expert career advisor.\n"
    "Analyze the following CV text and provide constructive recommendations for improving it, "
    "including skills, experience, and formatting suggestions.\n\n"
    f"{text}\n\n"
    "Please provide your recommendations as HTML with:\n"
    "- Important points in bold.\n"
    "- Use emojis/icons like ✅, 🔥, ⭐ where appropriate.\n"
    "- Highlight key words or phrases with inline CSS color styles (e.g., <span style='color:#10a37f'>green text</span>).\n"
    "Return only the HTML snippet, no additional explanation. and in final output give me errors and fix it""Break down the CV into sections like Summary, Experience, Skills, Education, and give:\n"
        "- A score out of 100 for each section\n"
        "- Use ✅ for good and ⚠️ for issues\n"
        "- Suggest inline fixes with stronger verbs or formatting tips\n"
        "- Format using HTML with <strong> and <span> for color.\n\n"

    )

    try:
        response = chat.send_message(prompt)
        recommendations = response.text
    except Exception as e:
        return jsonify({'error': f'AI processing failed: {str(e)}'}), 500

    return jsonify({'recommendations': recommendations})




@app.route('/interview', methods=['POST'])
def interview():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read file content in-memory
    file_stream = io.BytesIO(file.read())

    # Extract text based on file extension
    if file.filename.lower().endswith('.pdf'):
        try:
            text = extract_text_from_pdf(file_stream)
        except Exception as e:
            return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
    elif file.filename.lower().endswith(('.docx', '.doc')):
        try:
            text = extract_text_from_docx(file_stream)
        except Exception as e:
            return jsonify({'error': f'Failed to process DOCX: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    if not text.strip():
        return jsonify({'error': 'Could not extract text from the CV'}), 400

    # Prepare prompt for Gemini AI to analyze the CV
    prompt = (
     "You are a technical interviewer.\n"
        "Based on the following CV text, generate a list of 20 **technical** interview questions "
        "along with detailed model answers. Focus only on technical skills, tools, programming, "
        "and problem-solving relevant to the candidate's experience.\n\n"
        f"CV Text:\n{text}\n\n"
        "Format the output as:\n"
        "1. Question: ...\nAnswer: ...\n\n"
        "Provide clear, precise, and technical answers."
        "Please provide your recommendations as HTML with:\n"
    "- Important points in bold.\n"
    )

    try:
        response = chat.send_message(prompt)
        recommendations = response.text
    except Exception as e:
        return jsonify({'error': f'AI processing failed: {str(e)}'}), 500

    return jsonify({'recommendations': recommendations})


@app.route('/enhance_text', methods=['POST'])
def enhance_text():
    data = request.get_json()
    user_text = data.get('text', '')

    if not user_text:
        return jsonify({'error': 'Text is required'}), 400

    prompt = (
        "You're an expert editor.\n"
        "Improve the grammar, clarity, and wording of the following text. "
        "Use stronger verbs and more professional tone. "
        "Highlight fixes with emojis like ✅ for good changes and ⚠️ for needed improvements.\n\n"
        f"Text:\n{user_text}\n\n"
        "Return only the improved version as HTML with:\n"
        "- <strong> for fixes\n"
        "- <span style='color:green'> for good parts\n"
        "- <span style='color:orange'> for issues\n"
    )

    try:
        response = chat.send_message(prompt)
        improved = response.text
    except Exception as e:
        return jsonify({'error': f'AI failed: {str(e)}'}), 500

    return jsonify({'enhanced': improved})



def is_arabic(text):

    arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
    return len(arabic_chars) > len(text) * 0.4  # adjust threshold if needed

@app.route('/translate_auto', methods=['POST'])
def translate_auto():
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    if is_arabic(text):
        prompt = (
            f"Translate this Arabic sentence into Franco (Arabizi):\n{text}\n\n"
            "Just return the Franco version without extra explanation."
        )
    else:
        prompt = (
            f"Translate this Franco (Arabizi) sentence to Arabic:\n{text}\n\n"
            "Just return the Arabic translation without extra explanation."
        )

    try:
        response = chat.send_message(prompt)
        return jsonify({'translation': response.text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/medical_code_lookup', methods=['POST'])
def medical_code_lookup():
    data = request.get_json()
    code = data.get('code', '').strip()

    if not code:
        return jsonify({'error': 'Medical code is required'}), 400

    prompt = (
            f"Explain CPT code '{code}'\n"
   
    f"Include the full description , what services are included , when it's used , and what modifiers mean if present.\n"

    )

    try:
        response = chat.send_message(prompt)
        return jsonify({'meaning': response.text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/generate_webpage_code', methods=['POST'])
def generate_webpage_code():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    gemini_prompt = (
    f"Generate a complete single-page HTML, CSS, and JavaScript web page based on this description:\n"
    f"{prompt}\n\n"
    "Only return the full raw code of the page. Do NOT wrap it in triple backticks or markdown. No explanation. Just return plain code."
    )

    try:
        response = chat.send_message(gemini_prompt)
        return jsonify({'code': response.text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    # app.run(debug=True)
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
