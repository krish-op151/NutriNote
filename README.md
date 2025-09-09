# 🥗 NutriNote – AI-Powered WhatsApp Calorie Counter  
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)  [![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)](https://flask.palletsprojects.com/)  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-316192?logo=postgresql)](https://supabase.com/)  [![Redis](https://img.shields.io/badge/Redis-Cache-red?logo=redis)](https://redis.io/)  [![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-green?logo=twilio)](https://www.twilio.com/whatsapp)  [![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)](https://www.docker.com/)  [![Render](https://img.shields.io/badge/Deploy-Render.com-purple?logo=render)](https://render.com/) ![License](https://img.shields.io/badge/License-MIT-green.svg)

> Your personal nutrition buddy on WhatsApp. Log meals via **voice/text**, get instant calorie breakdowns, and track your health with ease!  

---

## 🚀 Introduction  
NutriNote is a **WhatsApp-based nutrition assistant**. Users simply send a **voice note or text**, and NutriNote:  
- Transcribes the input  
- Analyzes meals with AI  
- Estimates calories & macros  
- Stores results for long-term tracking  

This project demonstrates a **full-stack, event-driven app** integrating modern cloud services to solve a real-world problem.  

---

## ✨ Key Features  

- 🗣️ **Voice-First Logging** – Send meals via voice in natural language.  
- 📱 **WhatsApp Integration** – Powered by Twilio API.  
- 🤖 **AI-Powered Analysis** – Google Gemini 2.5 Flash for food recognition & calorie breakdown.  
- 🔊 **Speech-to-Text** – Google Cloud STT for transcription.  
- 💾 **Persistent Storage** – Supabase PostgreSQL.  
- 📊 **Daily Summaries** – `/summary` command for total calories & macros.  
- 📈 **Visual Feedback** – Macro pie charts via Matplotlib on WhatsApp.  
- ☁️ **Live Deployment** – Production-ready on Render.com with Docker.  

---

## 🛠️ Tech Stack  

- **Backend:** Python (Flask)  
- **AI Models:** Google Gemini 2.5 Flash, Google Cloud STT  
- **Database:** Supabase PostgreSQL  
- **Integration:** Twilio API for WhatsApp  
- **Cache:** Redis (for confirmations)  
- **Deployment:** Docker + Render  
- **Charts:** Matplotlib  

---

## 🏗️ System Architecture  

User on WhatsApp <--> Twilio API
|
v
Render.com Web Service (Flask App)
|
+---> Google Speech-to-Text (voice notes)
|
+---> Google Gemini API (nutrition analysis)
|
+---> Redis (temporary confirmation state)
|
+---> Supabase PostgreSQL (permanent storage)

---

## ⚙️ Local Setup & Installation  

### 🔑 Prerequisites  
- Python **3.10+**  
- Virtual environment (`venv`)  
- **FFmpeg** installed  
- Accounts: **Twilio**, **Google Cloud**, **Supabase**, **Render**  

1. **Clone the repository:**
```bash
git clone https://github.com/krish-op151/NutriNote.git
cd NutriNote
```

2. **Install Dependencies:**
```bash  
pip install -r requirements.txt
```

3. **Set Environment Variables:**
```bash  
Create a `.env` file in the root:  
```
**Twilio Credentials**
```bash
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token"
```
**Google Cloud Credentials**
```bash
GOOGLE_APPLICATION_CREDENTIALS="your-google-cloud-key-file.json"
```
**Gemini API Key**
```bash
GEMINI_API_KEY="your_gemini_api_key"
```
**Supabase Database URL**
```bash
DATABASE_URL="postgres://postgres:[PASSWORD]@[project].supabase.co:5432/postgres"
```
**Redis URL**
```bash
REDIS_URL="redis://localhost:6379"
```

4. **Run App**
```bash  
python app.py
```

5. **Expose with Ngrok**
```bash  
ngrok http 5000
```

**➡️ Update **Twilio WhatsApp Sandbox Webhook** with the Ngrok public URL.**  

---

## 🚀 Deployment  

- Deployed on **Render.com** using Docker.  
- Handles secrets via Render Dashboard.  
- Includes `ffmpeg` + all dependencies inside Dockerfile.  

---

## 🔮 Future Improvements  

- 📝 **User Corrections** – e.g., *“No, change to 3 rotis”*  
- ❓ **Nutrition Q&A** – Answer common food queries  
- 📅 **Weekly/Monthly Summaries** – Track progress over time  
- 🔘 **Interactive Buttons** – Twilio quick replies for Yes/No confirmations  

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
