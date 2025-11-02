# 🌍 GeoNation Agent

**GeoNation** is a Django-based Telex Agent that helps you identify the country a town or city belongs to. Simply input a place name (like *Lagos*, *Cairo*, or *Paris*) and it returns the corresponding country, along with latitude and longitude information.

Powered by [OpenStreetMap's Nominatim API](https://nominatim.org/), GeoNation delivers accurate and fast geographic lookups — no API key required.

---

## 🚀 Features

* Accepts a city or town name as input.
* Returns the country, latitude, and longitude.
* Uses OpenStreetMap’s Nominatim API (free & open).
* Implements Telex’s A2A (Agent-to-Agent) format.
* Built with Django, easily extendable for future use.

---

## 🧱 Requirements

* Python 3.9+
* Django 4.2+
* Requests library

Install dependencies:

```bash
pip install django requests
```

---

## ⚙️ Setup Instructions

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/geonation.git
cd geonation
```

### 2. Create a Django App

```bash
django-admin startproject geonation
python manage.py startapp agent
```

### 3. Add to Installed Apps

In `geonation/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'agent',
]
```

### 4. Create the View (agent/views.py)

```python
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def geonation_agent(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        payload = json.loads(request.body)
        query = payload.get("params", {}).get("query")
        if not query:
            return JsonResponse({"error": "Missing 'query' parameter"}, status=400)

        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
        headers = {"User-Agent": "GeoNation-Agent/1.0"}
        res = requests.get(url, headers=headers)

        if res.status_code != 200 or not res.json():
            return JsonResponse({"error": f"Could not find location for '{query}'"}, status=404)

        data = res.json()[0]
        country = data.get("display_name", "").split(",")[-1].strip()

        result = {
            "place": query,
            "country": country,
            "lat": data.get("lat"),
            "lon": data.get("lon"),
        }

        return JsonResponse({"result": result, "id": payload.get("id")})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
```

### 5. Configure URLs

In `agent/urls.py`:

```python
from django.urls import path
from .views import geonation_agent

urlpatterns = [
    path('', geonation_agent, name='geonation_agent'),
]
```

In `geonation/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('agent.urls')),
]
```

---

## 🧪 Testing Locally

Run your Django server:

```bash
python manage.py runserver 8000
```

Send a POST request:

```bash
curl -X POST http://127.0.0.1:8000/ \
-H "Content-Type: application/json" \
-d '{"method": "getCountry", "params": {"query": "Lagos"}}'
```

Expected response:

```json
{
  "result": {
    "place": "Lagos",
    "country": "Nigeria",
    "lat": "6.5244",
    "lon": "3.3792"
  },
  "id": null
}
```

---

## ☁️ Deployment

You can deploy GeoNation on any free Python host, such as:

* [Render](https://render.com)
* [Railway](https://railway.app)
* [PythonAnywhere](https://pythonanywhere.com)

Once deployed, you’ll get a public URL (e.g. `https://geonation.onrender.com/`).
This is the URL you’ll register as your **Agent Endpoint** on [Telex.im](https://telex.im/agents).

---

## 🔗 Telex Integration Steps

1. Go to [https://telex.im/agents](https://telex.im/agents)
2. Click **Connect Agent**
3. Fill in:

   * **Agent Name:** GeoNation
   * **Description:** Identify the country a city or town belongs to.
   * **Framework:** Python (Django)
   * **Endpoint:** your deployed URL
4. Click **Save** and Telex will automatically verify your endpoint.

---

## 🧠 Example Response

Request:

```json
{"method": "getCountry", "params": {"query": "Cairo"}}
```

Response:

```json
{
  "result": {
    "place": "Cairo",
    "country": "Egypt",
    "lat": "30.033",
    "lon": "31.233"
  }
}
```

---

## 🧰 License

This project is open source under the MIT License.

---

### 💡 Author

**Okumbor Franklin**
Email: [okumborfranklin@gmail.com](mailto:okumborfranklin@gmail.com)
Telex Username: `shadow_sama`
