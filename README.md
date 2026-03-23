# 🖖 Captain's Log: AI Travel Agent & Command Center

A full-stack, AI-powered travel planning application that acts as your personal command center. Built with Python and Streamlit, this app combines an agentic AI chat interface with a live-syncing Google Sheets database, document parsing (RAG), and dynamic PDF report generation.

---

## 🎯 Portfolio Highlights (Skills Demonstrated)
This project was built to demonstrate proficiency in modern Python development, AI integration, and DevOps:
* **Frontend Engineering:** Built interactive UIs, managed complex session state, and injected custom CSS styling using Streamlit.
* **Backend & Data:** Handled file I/O (PDF parsing), data manipulation (Pandas), and solved complex edge cases like Unicode encoding for European currencies (`fpdf2`).
* **Cloud & APIs:** Implemented secure server-to-server authentication (Service Accounts) to read/write from a live cloud database (Google Sheets API).
* **AI Engineering:** Designed Agentic workflows (LangChain) utilizing tools (Tavily Search) and implemented Retrieval-Augmented Generation (RAG) by dynamically injecting PDF text and UI state preferences into LLM prompts.
* **DevOps & Containerization:** Packaged the application into a secure, standalone Docker container for seamless, OS-agnostic deployment.

---

## ✨ Key Features

* **Agentic AI Chat:** Powered by Gemini 2.5 Flash and LangChain, the conversational agent can search the live web for travel data using Tavily and plan itineraries based on your custom preferences (Currency and Temperature).
* **Document RAG:** Drag and drop PDF booking confirmations (like flight tickets). The AI reads the document and uses that exact context to answer questions about your trip.
* **Cloud Database Sync:** A custom Python backend connects to a Google Sheets database via Service Account credentials. You can log expenses in the app's interactive data editor and push them directly to the cloud.
* **Dynamic PDF Briefing:** Automatically generates a formatted "Mission Briefing" PDF. It stitches together the AI's generated itinerary and your customized budget table, complete with robust Unicode character filtering for global currencies.
* **Interactive Dashboard:** Features dynamic expense charting, live map rendering (`geopy`), and a clean, custom-styled UI interface.

---

## 🛠️ Tech Stack

* **Frontend & UI:** Streamlit, Pandas
* **AI / LLM:** LangChain, Google Gemini API, Tavily Search API
* **Database / Cloud:** Google Sheets API (`gspread`)
* **Document Processing:** `pypdf` (reading context), `fpdf2` (writing reports)
* **Mapping:** `geopy`
* **Deployment:** Docker

---

## 🚀 Setup & Installation

You can run Captain's Log natively on your machine or inside a completely isolated Docker container. 

### 0. Pre-Flight Checklist (Required for both methods)
**1. Clone the Repository:**
    git clone git@github.com:itodorova1/captains-log.git
    cd captains-log

**2. Environment Variables:**
Create a `.env` file in the root directory and add your API keys so LangChain can access them:
    GEMINI_API_KEY=your_gemini_api_key_here
    TAVILY_API_KEY=your_tavily_api_key_here
You can generate API Keys from https://aistudio.google.com/api-keys 


**3. Google Sheets Database Setup:**
To enable the "Sync to Google Sheets" backend feature, you must configure a Google Cloud Service Account:
1. Go to the [Google Cloud Console](https://console.cloud.google.com) and enable the **Google Sheets API** and **Google Drive API**.
2. Create a **Service Account** and download the `credentials.json` key file to the root of this project. *(Note: This file is ignored by Git and Docker for security!)*
3. Create a new Google Sheet named exactly: `MyTrip_Budget_2026`.
4. **Crucial Step:** Click "Share" on your Google Sheet and invite the Service Account's robot email address as an **Editor**.

---

### Option A: Run Locally (Virtual Environment)
It is highly recommended to use a virtual environment:
    python -m venv venv
    source venv/bin/activate

Install the dependencies:
    pip install -r requirements.txt

Launch the Command Center:
    streamlit run app.py

---

### Option B: Run via Docker (Containerized)
Ensure you have Docker installed on your system.

**1. Build the container image:**
    docker build -t captains-log .

**2. Run the container (Choose your Operating System):**

*For Mac & Linux (Ubuntu/Debian):*
    docker run -p 8501:8501 --env-file .env -v $(pwd)/credentials.json:/app/credentials.json:ro captains-log

*For Linux (Fedora/SELinux users only):*
    docker run -p 8501:8501 --env-file .env -v $(pwd)/credentials.json:/app/credentials.json:ro,z captains-log

*For Windows (PowerShell):*
    docker run -p 8501:8501 --env-file .env -v "${PWD}/credentials.json:/app/credentials.json:ro" captains-log

*For Windows (Command Prompt):*
    docker run -p 8501:8501 --env-file .env -v "%cd%/credentials.json:/app/credentials.json:ro" captains-log

Open your browser and navigate to `http://localhost:8501`.

---

## 🗺️ Roadmap & Future Improvements
- [ ] **Smart Packing UI:** Add a 4th dashboard tab featuring an interactive `st.data_editor` luggage checklist (Clothes, Tech, Documents) that the AI can auto-populate based on the destination's weather forecast.
- [ ] **Google Sheets Multi-Tab Sync:** Expand the database integration to push and pull packing checklists to a secondary worksheet tab, allowing users to check off items on their mobile device while packing.
- [ ] **CI/CD Automation:** Implement GitHub Actions to automatically lint code and build/deploy the Docker container to the cloud on every push.
- [ ] **Multi-Agent Architecture:** Transition from a single generalist agent to a specialized team (Supervisor, Logistics, Guide, Finance) using advanced agentic frameworks like CrewAI.
- [ ] **Autonomous Tool Calling:** Empower the AI to execute Python functions that automatically write expenses to the Google Sheet without manual data entry.
- [ ] **Real-Time API Integrations:** Replace dummy UI data with live API calls (e.g., OpenWeatherMap for climate, Amadeus/SerpApi for live flight/hotel prices).
- [ ] **Two-Way Data Sync:** Implement a "Load from Cloud" feature to pull Google Sheets data *down* into the Streamlit UI, keeping devices perfectly synced.
- [ ] **Enterprise Backend Migration:** Transition from Google Sheets to a robust database like Supabase or PostgreSQL to support user authentication and multi-user scaling.
