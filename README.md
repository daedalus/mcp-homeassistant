# mcp-homeassistant

MCP server exposing Home Assistant 2026.4.1 REST API functionality.

[![PyPI](https://img.shields.io/pypi/v/mcp-homeassistant.svg)](https://pypi.org/project/mcp-homeassistant/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-homeassistant.svg)](https://pypi.org/project/mcp-homeassistant/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

mcp-name: io.github.daedalus/mcp-homeassistant

## Install

```bash
pip install mcp-homeassistant
```

## Configuration

Set the following environment variables:

- `HA_URL`: Home Assistant URL (default: http://localhost:8123)
- `HA_TOKEN`: Long-Lived Access Token (required)

## Usage

```bash
export HA_URL="http://homeassistant:8123"
export HA_TOKEN="your_long_lived_access_token"
mcp-homeassistant
```

## Tools

The MCP server exposes the following tools:

- `get_api_status` - Check if the API is running
- `get_config` - Get HA configuration
- `get_components` - List loaded components
- `get_events` - List event types and listener counts
- `get_services` - List available services by domain
- `get_states` - Get all entity states
- `get_state` - Get a specific entity state
- `set_state` - Update or create an entity state
- `delete_state` - Delete an entity state
- `fire_event` - Fire a custom event
- `call_service` - Call a Home Assistant service
- `render_template` - Render a Jinja template
- `get_history` - Get historical state changes
- `get_logbook` - Get logbook entries
- `check_config` - Validate configuration.yaml
- `handle_intent` - Handle an intent
- `get_error_log` - Get error log
- `get_calendars` - List calendar entities
- `get_calendar_events` - Get calendar events

## Resources

- `homeassistant://config` - Current config
- `homeassistant://states` - All entity states
- `homeassistant://services` - Available services
- `homeassistant://components` - Loaded components

## Development

```bash
git clone https://github.com/daedalus/mcp-homeassistant.git
cd mcp-homeassistant
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint
ruff check src/ tests/

# type check
mypy src/
```
