# PolyGlot AI - Advanced Language Translator Engine

An AI-powered, meaning-preserving language translation system built to bridge communication gaps with high contextual intelligence. Unlike traditional rule-based translation systems, PolyGlot AI utilizes Large Language Models (LLMs) to capture local idioms, cultural nuances, and original tones across multiple global and regional languages.

This project features an advanced **dual-framework microservices architecture**, combining the data persistence power of **Django** with the lightweight execution speed of **Flask** acting as the AI worker core.

---

##  Key Features

###  Context-Aware Translation

Uses cutting-edge Generative AI to preserve textual meaning, tone, formatting, and contextual intent across languages instead of merely substituting words.

### 👥 Dual-Framework Microservices Architecture

#### Django Gateway Service (Port 8000)

* Handles user requests and session management.
* Serves as the primary frontend gateway.
* Maintains translation history records.
* Provides database interaction and administrative control.

#### Flask AI Worker Service (Port 5000)

* Dedicated AI translation microservice.
* Processes translation requests independently.
* Communicates with Groq Cloud APIs.
* Executes prompt engineering and response generation.

###  Persistent Translation History

Stores:

* Original text
* Source language
* Target language
* Translated output
* Timestamps

All translation records are maintained using SQLite for easy auditing and retrieval.

### Multi-Language Support

Supports synchronized translations between:

* English
* Telugu (తెలుగు)
* Hindi (हिन्दी)
* Spanish (Español)
* French (Français)
* German (Deutsch)
* Japanese (日本語)
* Chinese (中文)
* Arabic (العربية)

###  Modern User Interface

Built using Tailwind CSS and Font Awesome with:

* Responsive design
* Character count tracking (up to 5000 characters)
* One-click language swapping
* Clipboard copy functionality
* Loading animations during translation
* Smooth asynchronous communication

---

##  Technology Stack

### Backend Frameworks

* Django 5.0.2
* Flask 3.0.2

### AI Infrastructure

* Groq Cloud API
* Llama 3.3 70B Versatile Model

```text
llama-3.3-70b-versatile
```

### Database

* SQLite3

### Frontend

* HTML5
* Tailwind CSS v4
* Font Awesome
* Vanilla JavaScript (ES6)

### Environment Management

* python-dotenv

---

##  Project Structure

```text
AI_LANGUAGE_TRANSLATOR_QGENAIPROJECT/
│
├── django_app/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── translator/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── translator/
│   │           └── index.html
│   │
│   ├── db.sqlite3
│   └── manage.py
│
├── flask_app/
│   ├── app.py
│   └── templates/
│       └── index.html
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## System Architecture Workflow

```text
                ┌──────────────────────────┐
                │      User Browser        │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │ Django Gateway Service   │
                │       Port : 8000        │
                └────────────┬─────────────┘
                             │
                  Async API Request
                             │
                             ▼
                ┌──────────────────────────┐
                │ Flask AI Worker Service  │
                │       Port : 5000        │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │       Groq Cloud API     │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │  Llama-3.3-70B Model     │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │ Translation Response     │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │ SQLite Translation Logs  │
                └──────────────────────────┘
```

---

##  Installation & Setup

###  Clone the Repository

```bash
git clone https://github.com/prabhasupriya/AI_LANGUAGE_TRANSLATOR_QGENAIPROJECT.git
cd AI_LANGUAGE_TRANSLATOR_QGENAIPROJECT
```

---

###  Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_secured_groq_api_key_here
FLASK_SECRET_KEY=your_alphanumeric_random_string_here
```

> The `.env` file is excluded through `.gitignore` and will never be pushed to GitHub.

---

###  Install Dependencies

```bash
pip install -r requirements.txt
```

---

###  Apply Database Migrations

```bash
cd django_app

python manage.py makemigrations

python manage.py migrate
```

---

##  Running the Application

This project uses two backend services.

Open two separate terminal windows.

---

### Terminal 1 — Start Flask AI Worker

```bash
cd flask_app

python app.py
```

Flask Service URL:

```text
http://127.0.0.1:5000
```

---

### Terminal 2 — Start Django Gateway

```bash
cd django_app

python manage.py runserver 8000
```

Django Service URL:

```text
http://127.0.0.1:8000
```

---

##  Security Considerations

### Environment Variable Isolation

Sensitive API keys remain outside source control using `.env` configuration files.

### Zero Client-Side Exposure

No API credentials are exposed in:

* HTML
* CSS
* JavaScript

All communication occurs securely through backend services.

### Secure Service Separation

Django and Flask operate independently, minimizing direct exposure of AI infrastructure.

---

##  Future Enhancements

* Voice-to-Text Translation
* Text-to-Speech Responses
* Translation History Dashboard
* PDF Export Support
* User Authentication System
* Translation Analytics
* Dark Mode Support
* Docker Containerization
* Redis Caching Layer
* PostgreSQL Production Deployment
* Translation Quality Evaluation Metrics

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit changes

```bash
git commit -m "Added new feature"
```

4. Push to GitHub

```bash
git push origin feature/new-feature
```

5. Create a Pull Request

---

## 🧑‍💻 Author

### Bandaru Prabha Supriya

* Computer Science Engineering Undergraduate
* Machine Learning & Deep Learning Enthusiast
* Full-Stack AI Application Developer
* Data Science Learner


---
### youtude video 
[you can watch here](https://youtu.be/gbpZDAA3TgU?si=ZHJXdSzsyzk4ZU0J)
##  Support

If you found this project useful or learned something from its architecture, consider giving the repository a ⭐ on GitHub.

Your support helps motivate future open-source AI projects and improvements.
