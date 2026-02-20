import json
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.calendar_service import create_event

app = FastAPI()

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
# Used only if you set a Server URL in Vapi dashboard (assistant-level webhook).
# This handles tool-calls sent by Vapi directly to your server.
@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    try:
        raw = await request.body()
        print(f"[Vapi Webhook RAW] {raw.decode()}")
        body = json.loads(raw)

        # Vapi wraps payload in a "message" key — fall back to body itself
        message = body.get("message", body)
        msg_type = message.get("type")

        print(f"[Vapi Webhook] type={msg_type}")

        if msg_type == "tool-calls":
            tool_calls = message.get("toolCallList", [])
            results = []

            for tool in tool_calls:
                tool_id = tool.get("id")
                fn_name = tool.get("function", {}).get("name")
                params  = tool.get("function", {}).get("arguments", {})

                # Vapi sometimes sends arguments as a JSON string — parse it
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                    except json.JSONDecodeError:
                        params = {}

                print(f"  -> tool_id={tool_id}, fn={fn_name}, params={params}")

                if fn_name == "schedule_meeting":
                    name  = params.get("name")
                    date  = params.get("date")
                    time  = params.get("time")
                    title = params.get("title")

                    if not name or not date or not time:
                        results.append({
                            "toolCallId": tool_id,
                            "result": f"Error: Missing required fields — name={name}, date={date}, time={time}"
                        })
                        continue

                    event = create_event(name=name, date=date, time=time, title=title)
                    results.append({
                        "toolCallId": tool_id,
                        "result": f"Meeting scheduled successfully! Calendar link: {event.get('htmlLink', 'N/A')}"
                    })

                else:
                    results.append({
                        "toolCallId": tool_id,
                        "result": f"Unknown tool: {fn_name}"
                    })

            return {"results": results}

        if msg_type in ("end-of-call-report", "transcript", "status-update"):
            print(f"  -> event logged: {msg_type}")
            return {"status": "received"}

        return {"status": "ok"}

    except Exception as e:
        print(f"[Vapi Webhook Error] {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# ─── SCHEDULE ─────────────────────────────────────────────────────────────────
# Vapi API Tool calls this endpoint directly when the assistant triggers
# the schedule_meeting tool (configured in Vapi Dashboard → Tools).
@app.post("/schedule")
async def schedule_meeting(request: Request):
    try:
        raw = await request.body()
        print(f"[Schedule RAW] {raw.decode()}")
        body = json.loads(raw)

        name  = body.get("name")
        date  = body.get("date")
        time  = body.get("time")
        title = body.get("title")

        print(f"[Schedule] name={name!r}, date={date!r}, time={time!r}, title={title!r}")

        if not name or not date or not time:
            print(f"[Schedule] ERROR: Missing required fields")
            return {
                "status": "error",
                "message": f"Missing required fields — name={name}, date={date}, time={time}"
            }

        event = create_event(name=name, date=date, time=time, title=title)

        print(f"[Schedule] SUCCESS — event link: {event.get('htmlLink')}")
        return {
            "status": "success",
            "event_id":   event.get("id"),
            "event_link": event.get("htmlLink"),
            "message":    f"Meeting scheduled for {name} on {date} at {time}. Calendar link: {event.get('htmlLink', 'N/A')}"
        }

    except Exception as e:
        print(f"[Schedule Error] {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }