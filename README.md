# CBIT Smart Chatbot

AI-powered chatbot system for **Chaitanya Bharathi Institute of Technology** that provides instant answers to student queries about admissions, fees, exams, placements, events, and more.

Built with **Django REST Framework** (backend) and **React** (frontend).

---

## Features

- **Smart NLP Engine** - Understands spelling mistakes, informal language, and synonyms
- **Conversation Memory** - Resolves follow-up questions ("What about its fees?")
- **Self-Learning System** - Admin answers teach the bot new responses automatically
- **Department Escalation** - Unanswered queries can be routed to HODs, Exam Cell, etc.
- **Admin Dashboard** - Analytics, intent management, chat history, and learning stats
- **Mobile-First PWA** - WhatsApp-style interface, works on any device
- **46 Pre-built Intents** across 8 categories (Admissions, Fees, Exams, Placements, Events, Faculty, Campus, General)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 4.2, Django REST Framework |
| Frontend | React 19, React Router 7, Axios, Recharts |
| Database | SQLite (development) |
| Auth | Token-based (DRF TokenAuthentication) |

---

## Prerequisites

Make sure these are installed on your system:

- **Python 3.11** - [Download](https://www.python.org/downloads/)
- **Node.js 22 or 24** - [Download](https://nodejs.org/)
- **Git** (optional) - [Download](https://git-scm.com/)

---

## Project Structure

```
Chat_bot/
├── backend/                  # Django REST API
│   ├── config/               # Django settings, root URLs
│   ├── chatbot/              # Main chatbot app
│   │   ├── api/              # Views, serializers, URLs
│   │   ├── services/         # NLP engine, spell correction, context resolver, learning
│   │   ├── models.py         # Database models
│   │   └── management/       # Seed data command
│   ├── accounts/             # Admin authentication
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 # React application
│   ├── public/               # Static assets, PWA manifest
│   ├── src/
│   │   ├── api/              # Axios API layer
│   │   ├── components/       # Chat & admin components
│   │   ├── context/          # Auth & Chat state management
│   │   ├── pages/            # Page components
│   │   └── styles/           # CSS files
│   └── package.json
└── README.md
```

---

## Setup & Installation

Open the project folder containing `backend` and `frontend`. Use two terminals.

### Backend on Windows PowerShell

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_intents
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 8000
```

Choose your own username and password when prompted. The database is created
locally by the migration command. Seeding adds the initial chatbot topics.

On macOS or Linux, create the environment with `python3 -m venv .venv` and use
`.venv/bin/python` for the Python commands.

### Frontend on Windows PowerShell

Open a second terminal from the project folder.

```powershell
cd frontend
npm.cmd ci --legacy-peer-deps
npm.cmd start
```

On macOS or Linux, use `npm` in place of `npm.cmd`.

Open [the home page](http://localhost:3000/). Choose **Student Chat** or
**Admin Login**. Keep both terminals running.

---

## How to Use

### For Students (Chat Interface)

1. Open http://localhost:3000/chat on your phone or laptop
2. Type a question like:
   - "What is the fee structure?"
   - "wen is exam" (handles spelling mistakes)
   - "Tell me about B.Tech CSE" → then "What about its fees?" (context memory)
3. Use quick action buttons: **Fees**, **Admission**, **Exam Dates**
4. After each answer, use: **Know More**, **Contact Us**, or **Back to Menu**

### For Admin (Dashboard)

1. Go to http://localhost:3000/login
2. Sign in with the account you created using `createsuperuser`.
3. **Dashboard** - View stats: sessions, messages, top intents, learning rate
4. **Intents** - Add/edit/delete questions and answers
5. **Categories** - Manage topic categories
6. **Chat History** - View all student conversations
7. **Unanswered Queries** - Answer queries to teach the bot, or escalate to departments

### Teaching the Bot (Learning System)

1. Go to **Admin > Unanswered Queries**
2. Click **Answer** on a pending query
3. Type the answer the bot should give
4. Click **Save & Teach Bot**
5. The bot will now answer similar questions automatically

---

## API Endpoints

### Public (No authentication required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Send a message and get bot response |
| POST | `/api/chat/session/` | Create a new chat session |
| GET | `/api/chat/session/<uuid>/history/` | Get session message history |
| GET | `/api/categories/public/` | List active categories |

### Admin (Token authentication required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard/stats/` | Dashboard analytics |
| GET/POST | `/api/admin/intents/` | List/Create intents |
| GET/PUT/DELETE | `/api/admin/intents/<id>/` | Intent CRUD |
| GET/POST | `/api/admin/categories/` | List/Create categories |
| GET | `/api/admin/chat-history/` | All chat sessions |
| GET | `/api/admin/fallbacks/` | Unanswered queries |
| POST | `/api/admin/fallbacks/<id>/answer/` | Answer & teach bot |
| POST | `/api/admin/fallbacks/<id>/escalate/` | Escalate to department |
| GET | `/api/admin/departments/` | List departments |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login (returns token) |
| POST | `/api/auth/logout/` | Logout (deletes token) |
| GET | `/api/auth/profile/` | Get user profile |

---

## Supported Query Categories

| # | Category | Example Queries |
|---|----------|----------------|
| 1 | **General** | "hi", "about cbit", "contact number", "college timings" |
| 2 | **Admissions & Courses** | "how to apply", "courses offered", "eligibility", "documents required" |
| 3 | **Fees & Scholarships** | "fee structure", "hostel fees", "scholarships", "how to pay fees" |
| 4 | **Exams & Schedules** | "exam schedule", "academic calendar", "internal marks", "results" |
| 5 | **Placements** | "placement stats", "top recruiters", "average package", "internships" |
| 6 | **Campus & Facilities** | "hostel", "library", "sports", "canteen", "wifi", "transport" |
| 7 | **Events & Activities** | "college fest", "sankranti sambaralu", "workshops", "student clubs" |
| 8 | **Faculty & Departments** | "professors", "HOD details", "departments", "principal" |

---

## NLP Capabilities

The chatbot handles:

```
"wen is exam"          →  Corrected to "when is exam"       →  exam_schedule
"fee structur"         →  Corrected to "fee structure"      →  fee_structure
"hw to apply for clg"  →  Corrected to "how to apply for college" →  admission_process
"hostle fee details"   →  Corrected to "hostel fee details" →  hostel_fees
```

**Follow-up Context:**
```
Student: "Tell me about the library"
Bot: [library info]
Student: "what are its timings?"           ← "its" resolved to "library"
Bot: [library timings]
```

**Synonym Understanding:**
```
"cost of course"    →  matches "fee structure" (cost = fees)
"job placement"     →  matches "placement stats" (job = placement)
"dorm room"         →  matches "hostel" (dorm = hostel)
```

---

## Troubleshooting

### Backend won't start
```bash
# Make sure virtual environment is activated
.venv\Scripts\Activate.ps1 # Windows PowerShell
source .venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt

# Re-run migrations
python manage.py migrate
```

### Frontend won't start

From the frontend folder, run `npm.cmd ci --legacy-peer-deps` again, then
`npm.cmd start`.

### CORS Error in Browser
Make sure the backend is running on port 8000 and frontend on port 3000. The CORS setting in `config/settings.py` allows `http://localhost:3000`.

### Database Reset
```bash
cd backend
# Delete existing database
del db.sqlite3          # Windows
rm db.sqlite3           # macOS/Linux

# Recreate
python manage.py migrate
python manage.py seed_intents
```

### Admin can't log in

Run `manage.py createsuperuser` with your virtual environment's Python if
you have yet to create an account. To reset an existing account's password,
run `manage.py changepassword <username>`.

---

## Production Deployment Notes

Set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS` in the
backend environment. Provide comma-separated hosts and set
`DJANGO_CORS_ALLOWED_ORIGINS` to the deployed frontend origin if the frontend
and backend use separate origins. Use `REACT_APP_API_URL` for the frontend's
backend URL, including the `/api` suffix. The host also needs HTTPS,
persistent database storage, and a way to serve the built frontend routes.

## License

This project was built for educational purposes at CBIT, Kadapa.
