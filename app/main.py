from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.calendar_service import create_event

app = FastAPI()

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",  # VS Code Live Server
        "http://localhost:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScheduleRequest(BaseModel):
    name: str
    date: str
    time: str
    title: Optional[str] = None


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ─── ROOT ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Voice Scheduling Agent is running"}


# ─── VAPI WEBHOOK ─────────────────────────────────────────────────────────────
# Vapi calls this when your assistant triggers a tool/function call.
# Set this URL in your Vapi dashboard -> Assistant -> Server URL:
#   http://<your-server>/vapi/webhook
@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    try:
        body = await request.json()
        msg_type = body.get("type")

        print(f"[Vapi] type={msg_type}")

        # Tool / function call from assistant
        if msg_type == "tool-calls":
            tool_calls = body.get("toolCallList", [])
            results = []

            for tool in tool_calls:
                fn_name = tool.get("function", {}).get("name")
                params  = tool.get("function", {}).get("arguments", {})

                print(f"  -> tool: {fn_name}, params: {params}")

                if fn_name == "create_event":
                    event = create_event(
                        name  = params.get("name"),
                        date  = params.get("date"),
                        time  = params.get("time"),
                        title = params.get("title"),
                    )
                    results.append({
                        "toolCallId": tool.get("id"),
                        "result": f"Event created! Link: {event.get('htmlLink', 'N/A')}"
                    })
                else:
                    results.append({
                        "toolCallId": tool.get("id"),
                        "result": f"Unknown tool: {fn_name}"
                    })

            return {"results": results}

        # End of call report / transcript events
        if msg_type in ("end-of-call-report", "transcript", "status-update"):
            print(f"  -> event logged: {msg_type}")
            return {"status": "received"}

        return {"status": "ok"}

    except Exception as e:
        print(f"[Vapi Webhook Error] {e}")
        return {"status": "error", "message": str(e)}


# ─── SCHEDULE (original endpoint — kept intact) ───────────────────────────────
@app.post("/schedule")
async def schedule_meeting(request: Request):
    try:
        body = await request.json()

        if not body:
            return {"status": "ready"}

        name  = body.get("name")
        date  = body.get("date")
        time  = body.get("time")
        title = body.get("title")

        if not name or not date or not time:
            return {"status": "ready"}

        event = create_event(
            name  = name,
            date  = date,
            time  = time,
            title = title
        )

        return {
            "status": "success",
            "event_id":   event.get("id"),
            "event_link": event.get("htmlLink")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }