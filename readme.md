AI Outage Monitor

A simple web app that tells you whether popular AI services are working properly, and explains any outages in plain English.

What is this?

This project checks the health of major AI platforms like OpenAI and Claude.

Instead of digging through technical status pages, this app:

Shows if systems are working or down

Lists recent outages

Explains what happened using AI

Think of it like a “health dashboard” for AI services.

Why did I build this?

Because status pages are confusing.

They show a lot of raw information, but not always in a way that’s easy to understand. This project turns that data into something simple and readable.

It’s also a practical way to demonstrate:

API integration

Real-time data processing

Basic reliability monitoring

Using AI to explain technical issues

What does it show?

When you open the app, you’ll see:

1. Current Status

Tells you if OpenAI and Claude are working or not.

2. Response Speed (Latency)

Shows how quickly each service responded.

Lower is better.

3. Availability

If everything is working, it shows 100%.

4. Recent Outages

For each provider, it shows:

What went wrong

When it started

When it ended

How long it lasted

Whether it was major or minor

5. Ask a Question

You can type a question like:

“Is there an outage right now?”

The app will explain the situation in simple terms.

How does it work?

Behind the scenes, the app does three things:

It calls official status APIs from OpenAI and Claude

It processes outage data (start time, end time, duration)

It uses AI to explain the results clearly

All of this happens in real time.

Project Structure
ai-outage-monitor/
│
├── app.py
├── requirements.txt
└── README.md

app.py → main application

requirements.txt → list of required packages

README.md → this file

How to run this project
Step 1 — Install Python

Make sure Python is installed on your computer.

Step 2 — Install dependencies

Open a terminal in the project folder and run:

pip install -r requirements.txt
Step 3 — Add your OpenAI API key

You need an API key from OpenAI.

Set it like this:

Windows

setx OPENAI_API_KEY "your_api_key_here"

Then restart your terminal.

Step 4 — Run the app
streamlit run app.py

If that doesn’t work:

python -m streamlit run app.py
Step 5 — Open in browser

The app will open automatically at:

http://localhost:8501
Live Demo

If deployed, you can access it here:

https://your-app-name.streamlit.app
Technologies Used

Python

Streamlit

Requests (for API calls)

OpenAI API (for explanations)

What this project demonstrates

This is a small but practical system that shows:

How to work with real-world APIs

How to process unreliable data

How to build a simple monitoring dashboard

How to integrate AI into a working product

Final thoughts

This project is intentionally simple.

It focuses on clarity, usefulness, and real-world behavior instead of complexity.

If it helps someone quickly understand whether an AI system is down, it has done its job.
