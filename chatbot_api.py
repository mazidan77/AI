# from flask import Flask, request, jsonify
# import google.generativeai as genai
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # Allow cross-origin requests (from frontend)

# # Configure Gemini API
# genai.configure(api_key="AIzaSyDS9tePm7YHqCSIVEzeuQ6DYX6XytbGQSg")
# model = genai.GenerativeModel('gemini-1.5-flash')
# chat = model.start_chat()

# @app.route('/chat', methods=['POST'])
# def chat_with_bot():
#     data = request.get_json()
#     user_message = data.get('message', '')

#     if not user_message:
#         return jsonify({'error': 'Message is required'}), 400

#     response = chat.send_message(user_message)
#     return jsonify({'response': response.text})

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import pdfplumber
import docx
import io

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




if __name__ == '__main__':
    app.run(debug=True)
