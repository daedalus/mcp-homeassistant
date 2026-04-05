# SPEC.md — mpc-homeassistant

## Purpose

An MCP (Model Context Protocol) server that exposes all Home Assistant 2026.4.1 REST API functionality as tools and resources, allowing AI assistants to interact with Home Assistant instances.

## Scope

### In Scope
- All REST API endpoints from Home Assistant 2026.4.1
- Tools for: states, services, events, history, logbook, config, components, templates, camera proxy, calendars, intents, error log
- Authentication via Long-Lived Access Token
- Connection configuration via environment variables or tool parameters

### Not in Scope
- WebSocket API (separate protocol)
- Streaming camera proxy
- Authentication flows (assumes pre-existing token)

## Public API / Interface

### Configuration
- `HA_URL`: Home Assistant URL (default: http://localhost:8123)
- `HA_TOKEN`: Long-Lived Access Token (required)

### Tools

| Tool | Endpoint | Description |
|------|----------|-------------|
| `get_api_status` | GET /api/ | Check if API is running |
| `get_config` | GET /api/config | Get Home Assistant configuration |
| `get_components` | GET /api/components | List loaded components |
| `get_events` | GET /api/events | List event types and listener counts |
| `get_services` | GET /api/services | List available services |
| `get_states` | GET /api/states | Get all entity states |
| `get_state` | GET /api/states/{entity_id} | Get specific entity state |
| `set_state` | POST /api/states/{entity_id} | Update or create entity state |
| `delete_state` | DELETE /api/states/{entity_id} | Delete entity state |
| `fire_event` | POST /api/events/{event_type} | Fire a custom event |
| `call_service` | POST /api/services/{domain}/{service} | Call a Home Assistant service |
| `render_template` | POST /api/template | Render a Jinja template |
| `get_history` | GET /api/history/period/{timestamp} | Get entity history |
| `get_logbook` | GET /api/logbook/{timestamp} | Get logbook entries |
| `check_config` | POST /api/config/core/check_config | Validate configuration.yaml |
| `handle_intent` | POST /api/intent/handle | Handle an intent |
| `get_error_log` | GET /api/error_log | Get error log |
| `get_calendars` | GET /api/calendars | List calendar entities |
| `get_calendar_events` | GET /api/calendars/{entity_id} | Get calendar events |
| `get_camera_proxy` | GET /api/camera_proxy/{entity_id} | Get camera image |

### Resources

| Resource | Description |
|----------|-------------|
| `homeassistant://config` | Current Home Assistant config |
| `homeassistant://states` | All entity states |
| `homeassistant://services` | Available services |
| `homeassistant://components` | Loaded components |

## Data Formats

### State Object
```json
{
  "entity_id": "string",
  "state": "string",
  "attributes": {},
  "last_changed": "ISO8601",
  "last_updated": "ISO8601"
}
```

### Service Call Request
```json
{
  "entity_id": "optional",
  "domain_specific_field": "value"
}
```

### Service Call Response
```json
{
  "changed_states": [],
  "service_response": {}
}
```

## Edge Cases

1. **Missing authentication** - Return 401 with clear error message
2. **Entity not found** - Return 404 when getting non-existent state
3. **Invalid service call** - Return 400 with service error details
4. **Network timeout** - Handle connection errors gracefully
5. **Camera entity not found** - Return appropriate error for invalid camera

## Performance & Constraints

- Single-threaded HTTP client (requests library)
- No caching of states (always fetch fresh)
- Timeout: 30 seconds per request

## Dependencies

- fastmcp (MCP server framework)
- requests (HTTP client)
- pydantic (data validation)
