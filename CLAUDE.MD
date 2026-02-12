# CLAUDE.MD

## Project Overview

Home Assistant custom integration for controlling a Renson Skye Pergola motorized roof. Deployed via HACS custom repository.

## Architecture

Python integration using aiohttp for REST API + WebSocket communication with the device's built-in web service. Uses `DataUpdateCoordinator` with 30s REST fallback and WebSocket push for real-time updates.

## Key Technologies

- **Python 3.12+** - Primary language
- **aiohttp** - Async HTTP client for REST API and WebSocket
- **Home Assistant** - DataUpdateCoordinator, CoordinatorEntity
- **pytest** - Testing framework with async support (pytest-asyncio)
- **JWT** - JSON Web Token authentication
- **HTTPS/SSL** - Self-signed certificates (verify_ssl=False)

## Development Guidelines

### Git Commit Practices

**IMPORTANT: Always commit working code before making major changes.**

1. **Commit Before Major Changes** - Create a safe rollback point before significant features, refactors, or breaking changes
2. **Commit Message Format** - Present tense verb (Add, Update, Fix, Refactor), under 72 chars
3. **What to Commit** - Only working code. Exclude `tests/test_config.json` (has real credentials)

## Testing Strategy

```bash
pytest tests/ -v -s          # All tests with output
pytest tests/test_client.py  # Specific file
pytest tests/test_client.py::TestRensonClient::test_login  # Specific test
```

- **Session-scoped authentication**: One login per test session, reused across tests
- **Rate limiting protection**: 2-second delays between lifecycle tests to avoid HTTP 429
- **Test configuration**: `tests/test_config.json` (gitignored, contains device credentials)
- Tests use `importlib.util` to load modules directly (no HA dependency in tests)

## Project Structure

```
ha-renson-embedded/
├── hacs.json                     # HACS custom repository config
├── custom_components/renson_embedded/
│   ├── api/                      # API client layer
│   │   ├── __init__.py          # Exports: RensonClient, RensonConfig
│   │   ├── client.py            # REST/WebSocket client with JWT auth
│   │   └── config.py            # RensonConfig dataclass
│   ├── __init__.py              # Integration setup/teardown
│   ├── binary_sensor.py         # Binary sensors (Fully Closed, Fully Opened)
│   ├── button.py                # Buttons (Fully Open, Fully Close, Open/Stop/Close/Stop cycle)
│   ├── config_flow.py           # Configuration flow (validates auth)
│   ├── const.py                 # Constants
│   ├── coordinator.py           # DataUpdateCoordinator (REST + WebSocket)
│   ├── cover.py                 # Cover entity (slide + tilt control, is_opening/is_closing)
│   ├── entity.py                # RensonEntity base class (shared DeviceInfo with web UI link)
│   ├── sensor.py                # Sensors (Roof State, Weather State)
│   ├── switch.py                # Switch (Roof Lock)
│   ├── manifest.json            # Integration metadata
│   ├── strings.json             # UI strings
│   └── translations/en.json     # Entity name translations (required for display)
└── tests/
```

## REST API Endpoints

All endpoints at `https://<host>/api/v1/...` with Bearer token auth.

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/authenticate` | `{"user_name":"...","user_pwd":"..."}` | Login, returns JWT |
| GET | `/skye2/roof/status` | - | Full roof status |
| GET | `/skye2/status` | - | Simplified status |
| PUT | `/skye2/roof/move` | `{"action":"stack","value":<0-100>}` | Set slide position |
| PUT | `/skye2/roof/move` | `{"action":"tilt","value":<degrees>}` | Set tilt angle |
| PUT | `/skye2/roof/stop` | `{}` | Stop all movement |
| PUT | `/skye2/roof/lock` | `"true"` or `"false"` (plain text) | Lock/unlock roof |
| GET | `/skye2/comfort/weather/state` | - | Weather state |

## WebSocket Protocol (wss://<host>/api/v1/ws/events)

- **Authenticate**: `{"type":"Authenticate","data":{"bearer":"<jwt>"}}`
- **Subscribe**: `{"type":"Subscribe","data":{"subscriptions":["ROOF_STATUS_CHANGED","SKYE2_STATUS_CHANGED","ROOF_SELF_TEST_STATUS_CHANGED","DIGITAL_INPUT_STATUS_CHANGED","SYSTEM_STATUS_CHANGED"]}}`
- **Ping**: `{"type":"Ping","data":{}}` every ~25s
- **Events**: `ROOF_STATUS_CHANGED` (full status with positions, motor details), `SKYE2_STATUS_CHANGED` (simplified with `roof_device.state`, `roof_device.direction`)

### WebSocket Direction Values (from `SKYE2_STATUS_CHANGED`)
- `roof_device.state`: `"moving"` or `"ready"`
- `roof_device.direction`: `"tilting_open"`, `"tilting_close"`, `"stacking"`, `"unstacking"`, `"idle"`

## Device Behavior

- **Device only processes one move command at a time** — sending a second command overrides the first
- **Closing tilt to 0° automatically closes the slide** — no need to send both commands
- **Opening stack automatically sets slats to 90°** — no need to send both commands
- **Slide position** (`stack`): 0-100% (device reports floats like 99.99, values are rounded to int)
- **Tilt angle** (`tilt`): 0-125° device range, mapped to HA 0-100 scale (device may report up to ~125.0005, clamped silently)
- **Negative values possible**: Device can report small negatives (e.g. -0.07°), handled by rounding/clamping
- Move commands return 202 Accepted (async operations)
- Self-signed SSL certificates (verify_ssl=False)
- Rate limits authentication requests (429 Too Many Requests)
- User types: "user", "professional", "renson technician"

## Entity Details

### Cover
- `is_closed`: Only checks stack (round(stack) == 0) — tilt not factored in to avoid toggle loop
- `is_opening`/`is_closing`: Uses `roof_device` from SKYE2_STATUS_CHANGED WebSocket events
- Open: sends stack to 100 (device auto-tilts to 90°)
- Close: sends tilt to 0 (device auto-closes slide)
- Tilt range: 0-125° mapped to HA 0-100; open tilt sends 90° (not max 125°)

### Binary Sensors
- **Fully Closed**: on when round(stack)==0 AND round(tilt)==0
- **Fully Opened**: on when round(stack)>=100 AND round(tilt)>=90

### Cycle Button (Open/Stop/Close/Stop)
- If moving → stop
- If stopped, last direction was opening (or fully open) → close (tilt to 0)
- If stopped, last direction was closing (or fully closed) → open (stack to 100)
- Tracks `_last_direction` from WebSocket updates; defaults to "closing" on startup

## Key Patterns

- `RensonEntity(CoordinatorEntity)` base class with shared `DeviceInfo` (includes `configuration_url` for web UI "Visit" button)
- Device identified by host IP in `DeviceInfo.identifiers`
- `entry_id` used for unique entity IDs
- Coordinator preserves `roof_device` WebSocket data across REST polls to prevent UI flickering
- When REST poll fails, `UpdateFailed` makes all entities unavailable automatically
- `ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)` instead of `ssl.create_default_context()` (avoids blocking)
- Client uses try/except for relative imports to support both HA and standalone tests
- Custom integrations need `translations/en.json` (not just `strings.json`) for entity names to display
