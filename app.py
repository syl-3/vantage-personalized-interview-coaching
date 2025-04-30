from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        job_description = request.form.get('job_description')
        interview_question = request.form.get('interview_question')

        if not job_description or not interview_question:
            session['error_message'] = "Please fill out both fields before submitting."
        else:
            ai_response = get_ai_response(job_description, interview_question)
            if ai_response.startswith("Error communicating with OpenAI:"):
                session['error_message'] = ai_response
            else:
                session['ai_response'] = ai_response
                session['last_question'] = interview_question

        return redirect(url_for('home'))

    # GET request
    ai_response = session.pop('ai_response', None)
    last_question = session.pop('last_question', None)
    error_message = session.pop('error_message', None)

    submitted = ai_response is not None

    return render_template(
        'index.html',
        submitted=submitted,
        ai_response=ai_response,
        last_question=last_question,
        error_message=error_message
    )



def get_ai_response(job_description, interview_question):
    try:
        prompt = (
    f"You are A.D. Vantage, a professional, calm, and serious interview preparation advisor. "
    f"Your communication style is confident, reflective, and focused. "
    f"You avoid overly friendly language, do not use exclamation points, and maintain a professional distance. "
    f"You often use phrases like 'I believe', 'It would be advisable', or 'You may want to consider' to reflect thoughtful, human-like judgment. "
    f"\n\nJob Posting Provided:\n{job_description}\n\n"
    f"Candidate's Question:\n{interview_question}\n\n"
    f"Please answer as if providing sincere, reasoned advice to a professional client. "
    f"Reference specific relevant aspects of the job description where applicable. "
    f"Begin with a brief orienting statement summarizing what the candidate is seeking to prepare for, then transition into specific, actionable advice."
    f"End without any excessive positivity or good-luck wishes."
)


        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )

        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
