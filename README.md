# SAMAY — Voice Scheduling Agent

> Real-time AI voice assistant that schedules Google Calendar events through natural conversation.

![Stack](https://img.shields.io/badge/Voice-VAPI-2D5A27?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-GPT--4o-3A86FF?style=flat-square)
![Calendar](https://img.shields.io/badge/Calendar-Google%20Calendar%20API-D4FC79?style=flat-square&logoColor=black)
![Deployed](https://img.shields.io/badge/Deployed-GitHub%20Pages-black?style=flat-square)

---

## 🌐 Deployed URL

**[https://hkgowda2974.github.io/Vikara-ai-assessment/](https://hkgowda2974.github.io/Vikara-ai-assessment/)**

### How to Test

1. Open the URL in Chrome (microphone access required)
2. Click the **green phone button** to start a voice call, or type in the text box
3. Allow microphone access when prompted
4. Speak naturally — for example:
   > *"Schedule a meeting called Project Review on March 5 at 2 PM"*
5. The agent will confirm the title, date, and time
6. The in-app calendar opens with the event highlighted
7. Click **"Open in Google Calendar"** to verify the live event was created

---

## 💻 Running Locally

### Prerequisites

- Python 3.9+
- Google Cloud project with **Calendar API** enabled
- `credentials.json` (OAuth 2.0) from Google Cloud Console
- VAPI account with an assistant configured

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/hkgowda2974/Vikara-ai-assessment.git
cd Vikara-ai-assessment

# 2. Install Python dependencies
pip install google-auth google-auth-oauthlib google-api-python-client flask

# 3. Place credentials.json in the project root, then run the backend
python calendar.py

# 4. Open index.html in your browser
# (or serve with any static server)
npx serve .
```

---

## 📅 Calendar Integration

The integration works in two layers:

### Layer 1 — VAPI Tool Call (Backend)

When the voice agent collects all required info (title, date, time), it fires a **tool call** to `calendar.py`. The backend:

- Authenticates with Google Calendar using stored OAuth 2.0 credentials
- Creates a real event via the **Google Calendar API v3**
- Returns the event's `htmlLink` and confirmed details back to the agent

### Layer 2 — Frontend Calendar View

The frontend listens for the keyword `MEETING_CONFIRMED` in the agent's speech. When detected:

- The in-app calendar navigates to the event's month and **highlights the correct date**
- The **"Open in Google Calendar"** button opens the exact day view
- The correct Google account is targeted using `?authuser=email` in the URL — no hardcoded account index, works regardless of sign-in order

### Tech Stack

| Component | Detail |
|-----------|--------|
| Voice | VAPI (real-time STT + TTS) |
| LLM | GPT-4o via VAPI |
| Calendar API | Google Calendar API v3 |
| Auth | OAuth 2.0 (offline access) |
| Backend | Python + google-api-python-client |
| Frontend | Vanilla HTML / CSS / JS |
| Deployment | GitHub Pages |
| Account targeting | `?authuser=` param (email-based, not index-based) |

---

## 🎙️ Conversation Flow

```
Agent  → "Hi! What would you like to schedule?"
User   → "A meeting called Project Review on March 5 at 2 PM"
Agent  → "Got it — Project Review, March 5, 2 PM. Scheduling now... MEETING_CONFIRMED"
Result → Calendar view opens with the event highlighted ✓
```

The keyword `MEETING_CONFIRMED` is the **sole trigger** for opening the calendar view — it never fires prematurely on partial information.

---

## 📸 Screenshots & Logs

### Debug Panel (live event data)
<img width="359" height="263" alt="image" src="https://github.com/user-attachments/assets/759e6b44-3e66-49ec-9a62-fd5dc17f696e" />
<img width="1343" height="435" alt="image" src="https://github.com/user-attachments/assets/97b22ec3-6e80-4808-b239-9f8e29da50bf" />




### Calendar View  of agent (correct date highlighted)
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/dbc207d7-e356-4701-9d61-cdccacf5b44c" />

### Calender View in google Calender 
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/1aa38c90-e9ad-4796-a906-4bd3009e6714" />


### Console Log Sample

```
[VAPI] Assistant said: You're meeting Mangoes is scheduled for February twenty sixth at three thirty PM. Meeting confirmed.
Vikara-ai-assessment/:1095 [VAPI] ✅ MEETING_CONFIRMED keyword detected in: You're meeting Mangoes is scheduled for February twenty sixth at three thirty PM. Meeting confirmed.
Vikara-ai-assessment/:1096 [VAPI] pendingEvent: null
Vikara-ai-assessment/:1097 [VAPI] allUserSpeech:  Hello Akas. Schedule a meeting. Burdenango On February twenty six. Three thirty PM. Mangoes.
Vikara-ai-assessment/:1149 [VAPI] → goCalendar: {title: 'Mangoes.', date: Thu Feb 26 2026 00:00:00 GMT+0530 (India Standard Time), time: '3:30 PM', gcalLink: null}
Vikara-ai-assessment/:989 [VAPI MESSAGE] type: conversation-update
Vikara-ai-assessment/:989 [VAPI MESSAGE] type: speech-update
Vikara-ai-assessment/:579 [SAMAY] goCalendar called with: {title: 'Mangoes.', date: Thu Feb 26 2026 00:00:00 GMT+0530 (India Standard Time), time: '3:30 PM', gcalLink: null}
Vikara-ai-assessment/:575 [DEBUG] title: Mangoes. | date: 2026/02/26 | time: 3:30 PM | source: speech-parse | url: https://calendar.google.com/calendar/r/day/2026/02/26?authuser=1mp22cs021%40gmail.com
Vikara-ai-assessment/:540 [SAMAY] state → calendar | scene classes: scene calendar
Vikara-ai-assessment/:984 [VAPI EVENT] speech-end
Vikara-ai-assessment/:821 [SAMAY] Opening Google Calendar: https://calendar.google.com/calendar/r/day/2026/02/26?authuser=1mp22cs021%40gmail.com (authuser: 1mp22cs021@gmail.com )
Vikara-ai-assessment/:989 [VAPI MESSAGE] type: status-update
```

---

## 📝 Notes

- The agent is pre-configured to schedule events on a specific Google Calendar (`1mp22cs021@gmail.com`). This is intentional for the demo — evaluators can verify a **live event was created** by clicking "Open in Google Calendar".
- The backend (`calendar.py`) requires OAuth credentials and runs separately from the static frontend.
- No sensitive API keys are exposed in the frontend — VAPI public keys are safe to include client-side by design.
- The debug overlay (top-right panel on the deployed site) shows full event metadata and can be dismissed by clicking ✕.
