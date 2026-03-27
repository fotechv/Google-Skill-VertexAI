# 🌤 Weather MCP Server

A **Model Context Protocol (MCP) server** that wraps the [OpenWeatherMap API](https://openweathermap.org/api), exposing 4 tools for real-time weather data. Runs locally via **STDIO transport** and integrates with Claude Desktop.

---

## Features

| Tool | Description |
|---|---|
| `get_current_weather` | Current conditions: temp, humidity, wind, pressure, visibility |
| `get_forecast` | 5-day / 3-hour forecast with hourly breakdown |
| `get_air_quality` | AQI (1–5 scale) + 8 pollutant concentrations |
| `get_weather_alerts` | Active severe weather warnings from official sources |

**Bonus:**
- ✅ **API key authentication** (MCP_API_KEY) with constant-time comparison
- ✅ Rate-limit awareness (55 calls/min, mirrors OWM free tier)
- ✅ Exponential backoff retry on network errors
- ✅ MCP Resources and Prompts (weather report, travel advice)

---

## Prerequisites

- Python **3.11+**
- A free [OpenWeatherMap API key](https://home.openweathermap.org/users/sign_up)
- Claude Desktop (for integration)

---

## Setup

### 1. Clone / navigate to the project

```bash
cd week3/server
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file (or export in your shell):

```bash
# Required
export OWM_API_KEY="your_openweathermap_api_key_here"

# Optional — enables MCP server auth
# If set, every tool call must include api_key="<this value>"
export MCP_API_KEY="your_secret_mcp_key_here"
```

> **Note:** OWM free tier keys can take up to 2 hours to activate after registration.

### 5. Test the server manually

```bash
python main.py
```

You should see in stderr:
```
Starting Weather MCP Server (STDIO transport)
Auth required: False
```

Press `Ctrl+C` to stop.

---

## Claude Desktop Integration

### 1. Find your Claude Desktop config file

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### 2. Add the server configuration

```json
{
  "mcpServers": {
    "weather": {
      "command": "/absolute/path/to/week3/server/.venv/bin/python",
      "args": ["/absolute/path/to/week3/server/main.py"],
      "env": {
        "OWM_API_KEY": "your_openweathermap_api_key_here",
        "MCP_API_KEY": "your_secret_mcp_key_here"
      }
    }
  }
}
```

> Replace paths with your actual absolute paths.  
> Remove `MCP_API_KEY` from the config if you don't want auth.

### 3. Restart Claude Desktop

After saving the config, fully quit and relaunch Claude Desktop. You should see the 🔨 tools icon in the input bar.

---

## Tool Reference

### `get_current_weather`

Get current weather for a city.

**Parameters:**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `city` | string | ✅ | — | City name, optionally with country code (`"Hanoi"` or `"London,GB"`) |
| `units` | string | ❌ | `metric` | `metric` (°C), `imperial` (°F), `standard` (K) |
| `api_key` | string | if auth | — | MCP server API key |

**Example input:**
```
What's the weather in Hanoi right now?
```

**Example output:**
```
🌍 Hanoi, VN
🌤 Condition: Partly cloudy
🌡 Temperature: 32°C (feels like 37°C)
   Min: 28°C | Max: 34°C
💧 Humidity: 75%
🌬 Wind: 3.5 m/s from SSE
☁ Cloud cover: 40%
🔵 Pressure: 1008 hPa
👁 Visibility: 10.0 km
```

---

### `get_forecast`

Get up to 5-day hourly forecast.

**Parameters:**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `city` | string | ✅ | — | City name |
| `days` | integer | ❌ | `5` | Number of days (1–5) |
| `units` | string | ❌ | `metric` | Temperature units |

**Example input:**
```
Show me the 3-day forecast for Tokyo in Fahrenheit.
```

---

### `get_air_quality`

Get AQI and pollutant breakdown.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `city` | string | ✅ | City name |

**AQI Scale:**
- 1 = Good ✅
- 2 = Fair 🟡
- 3 = Moderate 🟠
- 4 = Poor 🔴
- 5 = Very Poor ☠️

**Example input:**
```
How's the air quality in Beijing?
```

---

### `get_weather_alerts`

Get active severe weather warnings.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `city` | string | ✅ | City name |

**Example input:**
```
Are there any weather warnings for Miami right now?
```

---

## Authentication (Bonus)

When `MCP_API_KEY` is set, all tool calls require an `api_key` argument:

```
Get current weather for Paris. (api_key=your_secret_mcp_key_here)
```

The server uses **HMAC constant-time comparison** (`hmac.compare_digest`) to prevent timing attacks. The key is never logged or forwarded to upstream APIs.

---

## MCP Prompts

Two built-in prompts are available in Claude Desktop's prompt picker:

### `weather_report`
Generates a full weather briefing by calling all 4 tools and synthesizing results.

**Arguments:** `city` (required), `style` — formal / casual / broadcast (optional)

### `travel_weather_advice`
Weather-based packing and activity advice for a trip.

**Arguments:** `city` (required), `trip_duration` in days (optional, default 3)

---

## Project Structure

```
week3/
├── server/
│   ├── main.py              # Entrypoint — MCP server setup & handlers
│   ├── config.py            # Settings from environment variables
│   ├── auth.py              # API key verification (constant-time)
│   ├── http_client.py       # HTTP client: retry, backoff, rate limit
│   ├── mcp_definitions.py   # Tool, Resource, Prompt definitions
│   ├── requirements.txt
│   └── tools/
│       ├── current_weather.py
│       ├── forecast.py
│       ├── air_quality.py
│       └── weather_alerts.py
└── README.md
```

---

## Rate Limiting

The OWM free tier allows **60 calls/minute**. This server:
- Caps at **55 calls/minute** (conservative buffer)
- Returns a clear error message if the limit is hit: `"Rate limit reached. Please wait ~Xs"`
- Retries upstream 429 responses with exponential backoff

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `OWM_API_KEY not set` | Export the variable or add it to Claude Desktop config `env` |
| `401 Unauthorized` | Your OWM key may not be activated yet (wait up to 2 hours) |
| `404 Not Found` | Try a more specific city name, e.g. `"Ho Chi Minh City,VN"` |
| Tools not appearing in Claude | Restart Claude Desktop; check config JSON syntax |
| `python: command not found` | Use the full path to your venv Python in the config |

---

## References

- [MCP Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [MCP Inspector (debug tool)](https://github.com/modelcontextprotocol/inspector)
