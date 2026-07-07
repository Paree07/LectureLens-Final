# 🎓 LectureLens — AI-Powered Live Video Notes Assistant

LectureLens is an AI-powered learning assistant that helps students learn more effectively by generating intelligent notes from video lectures and meeting recordings.

Users can paste a YouTube lecture URL or upload a recording, while LectureLens processes the content and turns it into structured, useful notes — helping students focus on learning instead of constantly writing.

---

## 🌐 Live Demo

🚀 **Live Website:**  
https://lecture-lens-kappa.vercel.app

🔗 **Backend API:**  
https://lecturelens-production-5dec.up.railway.app

📚 **Interactive API Docs:**  
https://lecturelens-production-5dec.up.railway.app/docs

---

## ✨ Features

- 🎥 Process YouTube lecture videos
- 📤 Upload lecture or meeting recordings
- 🤖 AI-powered note generation
- 📝 Structured academic notes
- ⚡ Fast backend API processing
- 🎯 Clean and student-friendly interface
- 📱 Responsive frontend design
- ☁️ Fully deployed frontend and backend
- 🔗 Frontend–backend API integration

---

## 🛠️ Tech Stack

### Frontend

- React
- TypeScript
- Vite
- TSX
- Modern responsive UI

### Backend

- Python
- FastAPI
- Uvicorn
- Groq API
- YouTube Transcript API
- yt-dlp
- Faster Whisper

### Deployment

- Vercel — Frontend
- Railway — Backend
- GitHub — Version Control and Deployment Integration

---

## 🏗️ Project Structure

~~~text
LectureLens/
│
├── AI-Live-Video-Notes-Assistant/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   ├── utils/
│   │   │   └── main.py
│   │   ├── requirements.txt
│   │   └── railway.toml
│   │
│   ├── assets/
│   ├── docs/
│   └── frontend/
│
├── LectureLens Frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
~~~

---

## 🚀 Running the Project Locally

### 1. Clone the repository

~~~bash
git clone <your-repository-url>
cd LectureLens
~~~

### 2. Run the Backend

~~~bash
cd AI-Live-Video-Notes-Assistant/backend
python -m venv venv
~~~

Activate the virtual environment on Windows:

~~~bash
venv\Scripts\activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Create a `.env` file:

~~~env
GROQ_API_KEY=your_groq_api_key
~~~

Start the backend:

~~~bash
uvicorn app.main:app --reload
~~~

The local backend will be available at:

~~~text
http://127.0.0.1:8000
~~~

---

### 3. Run the Frontend

Open another terminal:

~~~bash
cd "LectureLens Frontend"
npm install
npm run dev
~~~

The local frontend will run on the URL shown by Vite.

---

## 🔐 Environment Variables

The backend requires:

~~~env
GROQ_API_KEY=your_groq_api_key
~~~

> Never commit your real API key or `.env` file to GitHub.

---

## ☁️ Deployment Architecture

~~~text
User
  │
  ▼
LectureLens Frontend
  │
  │ HTTPS API Requests
  ▼
Railway FastAPI Backend
  │
  ├── Groq AI
  ├── YouTube Transcript API
  ├── yt-dlp
  └── Faster Whisper
~~~

---

## 🔮 Future Improvements

- User authentication
- Saved lecture history
- Export notes as PDF
- AI-generated quizzes
- Flashcard generation
- Multi-language transcription
- Search across saved notes
- Personalized learning dashboard

---

## 👩‍💻 Author

**Paree07**

GitHub: https://github.com/Paree07

---

## ⭐ Support

If you find LectureLens useful, consider giving the repository a ⭐ on GitHub.

---
