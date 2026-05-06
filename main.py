"""
╔══════════════════════════════════════════════╗
║   📱 PHONE ASSISTANT API — Complete Code     ║
║   Siri જેવી API — FastAPI Python             ║
║   Features: Orders, Alarms, Messages, Weather║
╚══════════════════════════════════════════════╝

▶ LOCAL RUN:
    pip install fastapi uvicorn
    uvicorn main:app --reload --port 8000
    Browser: http://localhost:8000/docs

▶ PUBLISH ON RENDER:
    Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid, re

# ──────────────────────────────────────────────
# APP SETUP
# ──────────────────────────────────────────────
app = FastAPI(
    title="📱 Phone Assistant API",
    description="""
## Siri જેવી Phone Assistant API 🤖

### Features:
- 🛒 **Orders** — Food/Shopping order place કરો
- ⏰ **Alarms** — Alarm set/delete કરો  
- 💬 **Messages** — WhatsApp/SMS message મોકલો
- 🌤️ **Weather** — કોઈ પણ city નું weather જુઓ
- 🧠 **Smart Command** — Natural language command આપો

### Quick Test:
`POST /command` → `{"command": "order pizza from swiggy"}`
    """,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# DATABASE (In-Memory — Simple Dictionary)
# ──────────────────────────────────────────────
orders_db   = {}
alarms_db   = {}
messages_db = {}

# ──────────────────────────────────────────────
# MODELS (Request/Response Shapes)
# ──────────────────────────────────────────────

class OrderRequest(BaseModel):
    item:     str
    quantity: int    = 1
    platform: str    = "Swiggy"
    address:  str    = "Home"

class AlarmRequest(BaseModel):
    time:   str
    label:  str = "Alarm"
    repeat: str = "once"

class MessageRequest(BaseModel):
    to:       str
    text:     str
    platform: str = "WhatsApp"

class CommandRequest(BaseModel):
    command: str

# ──────────────────────────────────────────────
# HOME
# ──────────────────────────────────────────────
@app.get("/", tags=["🏠 Home"])
def home():
    return {
        "message": "👋 Phone Assistant API is LIVE!",
        "test_url": "/docs",
        "endpoints": {
            "🛒 orders":   "POST /orders",
            "⏰ alarms":   "POST /alarms",
            "💬 messages": "POST /messages",
            "🌤️ weather":  "GET  /weather/{city}",
            "🧠 command":  "POST /command  ← Smart shortcut!"
        }
    }

# ══════════════════════════════════════════════
# 🛒 ORDERS
# ══════════════════════════════════════════════
@app.post("/orders", tags=["🛒 Orders"])
def place_order(order: OrderRequest):
    """Food/Shopping order place કરો"""
    oid = str(uuid.uuid4())[:8].upper()
    record = {
        "order_id":  oid,
        "status":    "✅ Confirmed",
        "item":      order.item,
        "quantity":  order.quantity,
        "platform":  order.platform,
        "address":   order.address,
        "placed_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    orders_db[oid] = record
    return record

@app.get("/orders", tags=["🛒 Orders"])
def get_orders():
    """બધા orders જુઓ"""
    return {"total": len(orders_db), "orders": list(orders_db.values())}

@app.get("/orders/{order_id}", tags=["🛒 Orders"])
def get_one_order(order_id: str):
    """એક specific order જુઓ"""
    o = orders_db.get(order_id.upper())
    if not o:
        raise HTTPException(404, detail=f"Order '{order_id}' નથી મળ્યો")
    return o

@app.delete("/orders/{order_id}", tags=["🛒 Orders"])
def cancel_order(order_id: str):
    """Order cancel કરો"""
    o = orders_db.pop(order_id.upper(), None)
    if not o:
        raise HTTPException(404, detail="Order નથી મળ્યો")
    return {"message": f"❌ Order {order_id} cancel થઈ ગયો"}

# ══════════════════════════════════════════════
# ⏰ ALARMS
# ══════════════════════════════════════════════
@app.post("/alarms", tags=["⏰ Alarms"])
def set_alarm(alarm: AlarmRequest):
    """Alarm set કરો"""
    aid = "ALM-" + str(uuid.uuid4())[:6].upper()
    record = {
        "alarm_id":   aid,
        "time":       alarm.time,
        "label":      alarm.label,
        "repeat":     alarm.repeat,
        "status":     "🔔 Active",
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    alarms_db[aid] = record
    return record

@app.get("/alarms", tags=["⏰ Alarms"])
def get_alarms():
    """બધા alarms જુઓ"""
    return {"total": len(alarms_db), "alarms": list(alarms_db.values())}

@app.delete("/alarms/{alarm_id}", tags=["⏰ Alarms"])
def delete_alarm(alarm_id: str):
    """Alarm delete કરો"""
    a = alarms_db.pop(alarm_id.upper(), None)
    if not a:
        raise HTTPException(404, detail="Alarm નથી મળ્યો")
    return {"message": f"🗑️ Alarm {alarm_id} delete થઈ ગયો"}

# ══════════════════════════════════════════════
# 💬 MESSAGES
# ══════════════════════════════════════════════
@app.post("/messages", tags=["💬 Messages"])
def send_message(msg: MessageRequest):
    """Message send કરો"""
    mid = "MSG-" + str(uuid.uuid4())[:6].upper()
    record = {
        "message_id": mid,
        "to":         msg.to,
        "text":       msg.text,
        "platform":   msg.platform,
        "status":     "✉️ Sent",
        "sent_at":    datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    messages_db[mid] = record
    return record

@app.get("/messages", tags=["💬 Messages"])
def get_messages():
    """બધા messages જુઓ"""
    return {"total": len(messages_db), "messages": list(messages_db.values())}

# ══════════════════════════════════════════════
# 🌤️ WEATHER
# ══════════════════════════════════════════════
WEATHER_DATA = {
    "ahmedabad": {"city": "Ahmedabad", "temp": "38°C", "feel": "Hot 🥵",       "humidity": "25%", "wind": "12 km/h"},
    "surat":     {"city": "Surat",     "temp": "34°C", "feel": "Cloudy ⛅",    "humidity": "60%", "wind": "18 km/h"},
    "mumbai":    {"city": "Mumbai",    "temp": "32°C", "feel": "Humid 🌫️",    "humidity": "80%", "wind": "20 km/h"},
    "delhi":     {"city": "Delhi",     "temp": "40°C", "feel": "Very Hot 🔥",  "humidity": "30%", "wind": "10 km/h"},
    "bangalore": {"city": "Bangalore", "temp": "28°C", "feel": "Pleasant 🌤️", "humidity": "55%", "wind": "15 km/h"},
    "rajkot":    {"city": "Rajkot",    "temp": "37°C", "feel": "Sunny ☀️",    "humidity": "28%", "wind": "14 km/h"},
    "vadodara":  {"city": "Vadodara",  "temp": "36°C", "feel": "Warm 🌡️",     "humidity": "35%", "wind": "11 km/h"},
}

@app.get("/weather/{city}", tags=["🌤️ Weather"])
def get_weather(city: str):
    """City નું weather જુઓ"""
    data = WEATHER_DATA.get(city.lower().strip())
    if not data:
        return {
            "error":   f"'{city}' city નો data નથી",
            "available": list(WEATHER_DATA.keys())
        }
    return data

# ══════════════════════════════════════════════
# 🧠 SMART COMMAND (Natural Language)
# ══════════════════════════════════════════════
@app.post("/command", tags=["🧠 Smart Command"])
def smart_command(req: CommandRequest):
    """
    Natural language command — Siri style!

    Examples:
    - "order pizza from swiggy"
    - "set alarm at 7am"
    - "message Mummy good morning"
    - "weather in ahmedabad"
    """
    cmd = req.command.lower().strip()

    # ── ORDER ──────────────────────────────────
    if any(w in cmd for w in ["order", "buy", "get me"]):
        words    = re.sub(r'order|buy|get me|from|swiggy|zomato|amazon', '', cmd).split()
        item     = words[0].title() if words else "Item"
        platform = "Zomato" if "zomato" in cmd else ("Amazon" if "amazon" in cmd else "Swiggy")
        oid = str(uuid.uuid4())[:8].upper()
        record = {
            "order_id":  oid,
            "status":    "✅ Confirmed",
            "item":      item,
            "quantity":  1,
            "platform":  platform,
            "address":   "Home",
            "placed_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        orders_db[oid] = record
        return {"action": "🛒 ORDER_PLACED", "result": record}

    # ── ALARM ──────────────────────────────────
    if any(w in cmd for w in ["alarm", "wake", "remind"]):
        t = re.search(r'(\d{1,2}(?::\d{2})?(?:am|pm)?)', cmd)
        time_str = t.group(1) if t else "07:00"
        aid = "ALM-" + str(uuid.uuid4())[:6].upper()
        record = {
            "alarm_id":   aid,
            "time":       time_str,
            "label":      "Assistant Alarm",
            "repeat":     "once",
            "status":     "🔔 Active",
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        alarms_db[aid] = record
        return {"action": "⏰ ALARM_SET", "result": record}

    # ── MESSAGE ────────────────────────────────
    if any(w in cmd for w in ["message", "msg", "send", "whatsapp", "text"]):
        parts    = cmd.split()
        kws      = ["message", "msg", "send", "whatsapp", "text"]
        contact  = "Contact"
        body     = "Hello"
        for kw in kws:
            if kw in parts:
                i = parts.index(kw)
                if i + 1 < len(parts):
                    contact = parts[i + 1].title()
                    body    = " ".join(parts[i + 2:]) if i + 2 < len(parts) else "Hello"
        platform = "WhatsApp" if "whatsapp" in cmd else ("SMS" if "sms" in cmd else "WhatsApp")
        mid = "MSG-" + str(uuid.uuid4())[:6].upper()
        record = {
            "message_id": mid,
            "to":         contact,
            "text":       body,
            "platform":   platform,
            "status":     "✉️ Sent",
            "sent_at":    datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        messages_db[mid] = record
        return {"action": "💬 MESSAGE_SENT", "result": record}

    # ── WEATHER ────────────────────────────────
    if any(w in cmd for w in ["weather", "temperature", "temp", "rain", "forecast"]):
        found = next((c for c in WEATHER_DATA if c in cmd), None)
        if found:
            return {"action": "🌤️ WEATHER", "result": WEATHER_DATA[found]}
        return {"action": "🌤️ WEATHER", "message": "City name ના mળ્યો", "available_cities": list(WEATHER_DATA.keys())}

    # ── UNKNOWN ────────────────────────────────
    return {
        "action":  "❓ UNKNOWN",
        "message": f"Command સમજ ન આવ્યો: '{req.command}'",
        "try_these": [
            "order pizza from swiggy",
            "set alarm at 7am",
            "message Mummy good morning",
            "weather in ahmedabad"
        ]
    }
