from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uuid, re

app = FastAPI(
    title="Phone Assistant API",
    description="Siri like assistant API - Orders, Alarms, Messages, Weather",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orders_db   = {}
alarms_db   = {}
messages_db = {}

@app.get("/")
def home():
    return {
        "message": "Phone Assistant API is LIVE!",
        "docs": "/docs",
        "endpoints": ["/orders", "/alarms", "/messages", "/weather/{city}", "/command"]
    }

@app.post("/orders")
def place_order(item: str, quantity: int = 1, platform: str = "Swiggy", address: str = "Home"):
    oid = str(uuid.uuid4())[:8].upper()
    record = {
        "order_id":  oid,
        "status":    "Confirmed",
        "item":      item,
        "quantity":  quantity,
        "platform":  platform,
        "address":   address,
        "placed_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    orders_db[oid] = record
    return record

@app.get("/orders")
def get_orders():
    return {"total": len(orders_db), "orders": list(orders_db.values())}

@app.get("/orders/{order_id}")
def get_one_order(order_id: str):
    o = orders_db.get(order_id.upper())
    if not o:
        raise HTTPException(404, detail="Order not found")
    return o

@app.delete("/orders/{order_id}")
def cancel_order(order_id: str):
    o = orders_db.pop(order_id.upper(), None)
    if not o:
        raise HTTPException(404, detail="Order not found")
    return {"message": f"Order {order_id} cancelled"}

@app.post("/alarms")
def set_alarm(time: str, label: str = "Alarm", repeat: str = "once"):
    aid = "ALM-" + str(uuid.uuid4())[:6].upper()
    record = {
        "alarm_id":   aid,
        "time":       time,
        "label":      label,
        "repeat":     repeat,
        "status":     "Active",
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    alarms_db[aid] = record
    return record

@app.get("/alarms")
def get_alarms():
    return {"total": len(alarms_db), "alarms": list(alarms_db.values())}

@app.delete("/alarms/{alarm_id}")
def delete_alarm(alarm_id: str):
    a = alarms_db.pop(alarm_id.upper(), None)
    if not a:
        raise HTTPException(404, detail="Alarm not found")
    return {"message": f"Alarm {alarm_id} deleted"}

@app.post("/messages")
def send_message(to: str, text: str, platform: str = "WhatsApp"):
    mid = "MSG-" + str(uuid.uuid4())[:6].upper()
    record = {
        "message_id": mid,
        "to":         to,
        "text":       text,
        "platform":   platform,
        "status":     "Sent",
        "sent_at":    datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    messages_db[mid] = record
    return record

@app.get("/messages")
def get_messages():
    return {"total": len(messages_db), "messages": list(messages_db.values())}

WEATHER_DATA = {
    "ahmedabad": {"city": "Ahmedabad", "temp": "38C", "feel": "Hot",       "humidity": "25%"},
    "surat":     {"city": "Surat",     "temp": "34C", "feel": "Cloudy",    "humidity": "60%"},
    "mumbai":    {"city": "Mumbai",    "temp": "32C", "feel": "Humid",     "humidity": "80%"},
    "delhi":     {"city": "Delhi",     "temp": "40C", "feel": "Very Hot",  "humidity": "30%"},
    "bangalore": {"city": "Bangalore", "temp": "28C", "feel": "Pleasant",  "humidity": "55%"},
    "rajkot":    {"city": "Rajkot",    "temp": "37C", "feel": "Sunny",     "humidity": "28%"},
}

@app.get("/weather/{city}")
def get_weather(city: str):
    data = WEATHER_DATA.get(city.lower().strip())
    if not data:
        return {"error": f"City '{city}' not found", "available": list(WEATHER_DATA.keys())}
    return data

@app.get("/command")
def smart_command(q: str):
    cmd = q.lower().strip()

    if any(w in cmd for w in ["order", "buy"]):
        words = re.sub(r'order|buy|from|swiggy|zomato|amazon', '', cmd).split()
        item  = words[0].title() if words else "Item"
        platform = "Zomato" if "zomato" in cmd else ("Amazon" if "amazon" in cmd else "Swiggy")
        oid = str(uuid.uuid4())[:8].upper()
        record = {"order_id": oid, "status": "Confirmed", "item": item, "platform": platform,
                  "placed_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
        orders_db[oid] = record
        return {"action": "ORDER_PLACED", "result": record}

    if any(w in cmd for w in ["alarm", "wake"]):
        t = re.search(r'(\d{1,2}(?::\d{2})?(?:am|pm)?)', cmd)
        time_str = t.group(1) if t else "07:00"
        aid = "ALM-" + str(uuid.uuid4())[:6].upper()
        record = {"alarm_id": aid, "time": time_str, "status": "Active",
                  "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
        alarms_db[aid] = record
        return {"action": "ALARM_SET", "result": record}

    if any(w in cmd for w in ["message", "msg", "whatsapp"]):
        parts = cmd.split()
        contact, body = "Contact", "Hello"
        for kw in ["message", "msg", "whatsapp"]:
            if kw in parts:
                i = parts.index(kw)
                if i + 1 < len(parts):
                    contact = parts[i+1].title()
                    body    = " ".join(parts[i+2:]) if i+2 < len(parts) else "Hello"
        mid = "MSG-" + str(uuid.uuid4())[:6].upper()
        record = {"message_id": mid, "to": contact, "text": body, "status": "Sent",
                  "sent_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
        messages_db[mid] = record
        return {"action": "MESSAGE_SENT", "result": record}

    if any(w in cmd for w in ["weather", "temperature"]):
        found = next((c for c in WEATHER_DATA if c in cmd), None)
        if found:
            return {"action": "WEATHER", "result": WEATHER_DATA[found]}
        return {"action": "WEATHER", "available": list(WEATHER_DATA.keys())}

    return {
        "action": "UNKNOWN",
        "try": ["order pizza", "set alarm at 7am", "message Mummy hello", "weather ahmedabad"]
    }
