"""
This code imports the necessary modules and libraries for a Flask web application that will render 
templates using OpenAI and accept user input through HTML forms.
"""

import subprocess, sys
from flask import Flask, render_template_string, request


try:
    import openai
except ImportError:
    print("openai package not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    import openai
    

# Sets the API key for the OpenAI API using the value of the 'OPENAI_API_KEY' environment variable.  
from config import OPENAI_API_KEY

# Imports the API key for the OpenAI API using the value of the 'OPENAI_API_KEY' from the config file.  
openai.api_key = OPENAI_API_KEY

# This code uses the OpenAI API to generate a resume
def tailor_resume(job_description, skills_required, current_resume):
    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an expert resume tailoring assistant."},
        {"role": "user", "content": f"""
        Job Description: {job_description}
        
        Skills Required: {skills_required}
        
        Current Resume: {current_resume}
        
        Please tailor the current resume to match the job description and required skills. 
        Highlight relevant experiences and skills, and add any missing key skills if the applicant might reasonably have them. 
        Format the resume professionally and ensure it's ATS-friendly.
        """}
    ])
    return response.choices[0].message.content

# Create a Flask web application object named app and define a route for the root URL that responds to GET and POST requests
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def home():
    tailored_resume = ""
    if request.method == 'POST':
        job_description = request.form['job_description']
        skills_required = request.form['skills_required']
        current_resume = request.form['current_resume']
        tailored_resume = tailor_resume(job_description, skills_required, current_resume)

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Tailoring Expert</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" />
        <style>
            .form-group { margin-bottom: 15px; }
        </style>
        <script>
        async function tailorResume() {
            const output = document.querySelector("#output");
            output.textContent = "Tailoring your resume...";
            const response = await fetch("/tailor", {
                method: "POST",
                body: new FormData(document.querySelector("#resume-form")),
            });
            const newOutput = await response.text();
            output.textContent = newOutput;
        }
        function copyToClipboard() {
            const output = document.querySelector("#output");
            const textarea = document.createElement("textarea");
            textarea.value = output.textContent;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);
            alert("Copied to clipboard");
        }
        </script>
    </head>
    <body>
        <div class="container">
            <h1 class="my-4">Resume Tailoring Expert</h1>
            <form id="resume-form" onsubmit="event.preventDefault(); tailorResume();" class="mb-3">
                <div class="form-group">
                    <label for="job_description">Job Description:</label>
                    <textarea class="form-control" id="job_description" name="job_description" rows="4" required></textarea>
                </div>
                <div class="form-group">
                    <label for="skills_required">Skills Required:</label>
                    <input type="text" class="form-control" id="skills_required" name="skills_required" required>
                </div>
                <div class="form-group">
                    <label for="current_resume">Current Resume:</label>
                    <textarea class="form-control" id="current_resume" name="current_resume" rows="10" required></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Tailor Resume</button>
            </form>
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    Tailored Resume:
                    <button class="btn btn-secondary btn-sm" onclick="copyToClipboard()">Copy</button>
                </div>
                <div class="card-body">
                    <pre id="output" class="mb-0" style="white-space: pre-wrap">{{ tailored_resume }}</pre>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', tailored_resume=tailored_resume)

# Create a Flask web application object named app and define a route for the root URL that responds to GET and POST requests
@app.route('/tailor', methods=['POST'])
def tailor():
    job_description = request.form['job_description']
    skills_required = request.form['skills_required']
    current_resume = request.form['current_resume']
    return tailor_resume(job_description, skills_required, current_resume)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)