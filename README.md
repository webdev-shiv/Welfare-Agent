# Government Scheme Welfare Agent Portal

Welcome to the **Government Scheme Welfare Agent Portal** repository. This is an integrated platform featuring a React-based interactive web frontend and an Agent Development Kit (ADK) multi-agent backend powered by Gemini.

<p align="center">
  <img src="welfare-agent/assets/cover_page_banner.png" alt="Welfare Agent Cover Banner" width="800"/>
</p>

## 📂 Repository Structure

This repository is split into two main sections:

1. **[frontend/](file:///c:/Users/shiva/OneDrive/Desktop/capstone%20project/goverment%20scheme/frontend)**
   - A modern React + Vite application implementing the Citizen Dashboard, WhatsApp-style AI coordinator assistant, Document Vault, NGO portal, and Admin configurations.
   - Includes full accessibility settings (screen reader narration, high contrast mode, text resizing, and multi-language English/Hindi toggle).

2. **[welfare-agent/](file:///c:/Users/shiva/OneDrive/Desktop/capstone%20project/goverment%20scheme/welfare-agent)**
   - The core ADK agent codebase housing the coordinator and its 8 specialized sub-agents.
   - Handles advanced scheme search indexing, multi-criteria eligibility calculations, security checks, and fraud scoring.

---
Workflow :
<img width="1024" height="1024" alt="Image" src="https://github.com/user-attachments/assets/fa57efbe-c28a-4b56-b00a-2034f447705a" />
## 🚀 Quick Start Guide

Follow these steps to run the complete stack locally.

### Step 1: Clone and Navigate
If you haven't already, navigate into the project workspace:
```bash
cd "goverment scheme"
```

### Step 2: Configure Environment Variables
Copy the environment template in the agent folder and fill in your **Gemini API Key**:
```bash
cp welfare-agent/.env.example welfare-agent/.env
# Open welfare-agent/.env and add your GOOGLE_API_KEY / GEMINI_API_KEY
```

### Step 3: Run the Backend (Agent & FastAPI)
Inside the `welfare-agent` folder:
```bash
cd welfare-agent
make install
make run
```
The backend API server will start on **`http://localhost:8000`**.

### Step 4: Run the Frontend (React UI)
In a new terminal, inside the `frontend` folder:
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to the dev server link (usually **`http://localhost:5173`**).

---

## 🛡️ Security Warning
> [!WARNING]
> Never commit your `.env` files or expose your Gemini API keys to GitHub. Our root `.gitignore` is pre-configured to keep these credentials secure.
