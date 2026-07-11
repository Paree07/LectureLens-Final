# 🎓 LectureLens — AI-Powered Live Video Notes Assistant

LectureLens is an AI-powered learning platform that transforms YouTube lectures and uploaded videos into structured study material. It automatically generates transcripts, AI-powered notes, key concepts, flashcards, quizzes, and provides an AI chat assistant to help students learn more effectively.

🌐 **Live Demo:** https://lecture-lens-final.vercel.app

---

# ✨ Features

## 📺 YouTube Lecture Analysis
- Analyze any public YouTube lecture
- Fetch video metadata
- Display embedded video player
- Automatic transcript generation

## 🤖 AI Learning Workspace
- AI-generated lecture summaries
- Live Notes
- Complete Transcript
- Key Concepts extraction
- Study Tips
- Topic Overview

## 💬 AI Chat
- Ask questions about the lecture
- Context-aware responses
- Personalized explanations

## 📝 Flashcards
- Automatic flashcard generation
- Quick revision mode
- AI-generated question-answer cards

## 🧠 Quiz Generator
- Multiple Choice Questions
- Instant answer validation
- AI-generated assessments

## 📁 Upload Your Own Lectures
Supports:
- MP4
- MP3
- WAV
- M4A

Generate notes and transcripts from uploaded lecture recordings.

## 📚 Study Tools
- Export Notes as PDF
- Copy Notes
- Bookmark Lectures
- Share Notes
- Lecture History
- Download History

## 📱 Responsive Design
- Desktop
- Tablet
- Mobile
- Cross-browser compatible

---

# 🛠 Tech Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Lucide Icons

## Backend

- FastAPI
- Python
- Uvicorn

## AI

- Groq API
- Faster Whisper
- YouTube Transcript API

## Video Processing

- yt-dlp

## Deployment

Frontend:
- Vercel

Backend:
- Railway

---

# 📂 Project Structure

```
LectureLens-Final
│
├── LectureLens Frontend
│   ├── src
│   ├── public
│   ├── components
│   ├── pages
│   └── services
│
├── AI-Live-Video-Notes-Assistant
│   └── backend
│       ├── api
│       ├── services
│       ├── uploads
│       ├── outputs
│       └── main.py
│
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/Paree07/LectureLens-Final.git
```

---

## Frontend

```bash
cd "LectureLens Frontend"

npm install

npm run dev
```

Frontend runs on

```
http://localhost:5173
```

---

## Backend

```bash
cd AI-Live-Video-Notes-Assistant/backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs on

```
http://127.0.0.1:8000
```

---

# 🔑 Environment Variables

## Frontend (.env)

```env
VITE_API_BASE_URL=https://YOUR-RAILWAY-URL.up.railway.app
```

---

## Backend (.env)

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY

SUPADATA_API_KEY=YOUR_SUPADATA_API_KEY
```

---

# 🌍 Live Deployment

Frontend

https://lecture-lens-final.vercel.app

Backend

https://lecturelens-final-production.up.railway.app

---

# 📌 Major Functionalities

✔ Analyze YouTube Lectures

✔ Generate AI Notes

✔ Generate Transcript

✔ Extract Key Concepts

✔ AI Chat

✔ Flashcards

✔ Quiz Generation

✔ Upload Lecture Files

✔ PDF Export

✔ Bookmark Lectures

✔ Download History

✔ Responsive Design

✔ Railway Deployment

✔ Vercel Deployment

---

# 🎯 Future Improvements

- User Authentication
- Cloud Storage
- Multi-language Support
- Lecture Recommendations
- Voice Chat
- Real-time Collaboration
- Offline Mode
- Note Synchronization

---

# 👨‍💻 Author

**Pari**

GitHub

https://github.com/Paree07

---

# ⭐ If you like this project

Give the repository a ⭐ on GitHub!

---

# 📄 License

This project is developed for educational and academic purposes.
