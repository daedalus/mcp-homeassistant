import os
from typing import Any

import fastmcp
import requests
from pydantic import BaseModel

mcp = fastmcp.FastMCP("mpc-homeassistant")


def _get_ha_url() -> str:
    return os.getenv("HA_URL", "http://localhost:8123")


def _get_ha_token() -> str:
    token = os.getenv("HA_TOKEN", "")
    if not token:
        raise ValueError("HA_TOKEN environment variable is required")
    return token


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_ha_token()}",
        "Content-Type": "application/json",
    }


class Config(BaseModel):
    components: list[str]
    config_dir: str
    elevation: int
    latitude: float
    location_name: str
    longitude: float
    time_zone: str
    unit_system: dict[str, str]
    version: str
    whitelist_external_dirs: list[str]


class State(BaseModel):
    entity_id: str
    state: str
    attributes: dict[str, Any]
    last_changed: str
    last_updated: str


class ServiceInfo(BaseModel):
    domain: str
    services: list[str]


class EventInfo(BaseModel):
    event: str
    listener_count: int


class CalendarInfo(BaseModel):
    entity_id: str
    name: str


class CalendarEvent(BaseModel):
    summary: str
    start: dict[str, str]
    end: dict[str, str]
    description: str | None = None
    location: str | None = None


@mcp.tool()
def get_api_status() -> dict[str, str]:
    """Check if the Home Assistant API is running.

    Returns:
        A dictionary containing the API status message.

    Example:
        >>> get_api_status()
        {"message": "API running."}
    """
    response = requests.get(f"{_get_ha_url()}/api/", headers=_get_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_config() -> dict[str, Any]:
    """Get the current Home Assistant configuration.

    Returns:
        A dictionary containing the HA configuration including components,
        location, unit system, and version.

    Example:
        >>> get_config()
        {"components": [...], "version": "2026.4.1", ...}
    """
    response = requests.get(
        f"{_get_ha_url()}/api/config", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_components() -> list[str]:
    """Get list of currently loaded components.

    Returns:
        A list of component names loaded in Home Assistant.

    Example:
        >>> get_components()
        ["sensor.cpuspeed", "frontend", "config.core", ...]
    """
    response = requests.get(
        f"{_get_ha_url()}/api/components", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_events() -> list[EventInfo]:
    """Get list of event types and their listener counts.

    Returns:
        A list of event info objects with event name and listener count.

    Example:
        >>> get_events()
        [{"event": "state_changed", "listener_count": 5}, ...]
    """
    response = requests.get(
        f"{_get_ha_url()}/api/events", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_services() -> list[ServiceInfo]:
    """Get list of available services organized by domain.

    Returns:
        A list of service info objects organized by domain.

    Example:
        >>> get_services()
        [{"domain": "browser", "services": ["browse_url"]}, ...]
    """
    response = requests.get(
        f"{_get_ha_url()}/api/services", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_states() -> list[State]:
    """Get all entity states in Home Assistant.

    Returns:
        A list of all entity states with their current values and attributes.

    Example:
        >>> get_states()
        [{"entity_id": "sun.sun", "state": "below_horizon", ...}, ...]
    """
    response = requests.get(
        f"{_get_ha_url()}/api/states", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_state(entity_id: str) -> State:
    """Get the state of a specific entity.

    Args:
        entity_id: The entity ID to retrieve (e.g., 'sensor.kitchen_temperature').

    Returns:
        The state object for the requested entity.

    Raises:
        requests.HTTPError: If the entity is not found (404).

    Example:
        >>> get_state("sensor.kitchen_temperature")
        {"entity_id": "sensor.kitchen_temperature", "state": "22.5", ...}
    """
    response = requests.get(
        f"{_get_ha_url()}/api/states/{entity_id}", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def set_state(
    entity_id: str, state: str, attributes: dict[str, Any] | None = None
) -> State:
    """Update or create the state of an entity.

    Note: This sets the representation of a device within Home Assistant
    and will not communicate with the actual device. To communicate with
    the device, use the call_service tool.

    Args:
        entity_id: The entity ID to set (e.g., 'sensor.kitchen_temperature').
        state: The state value (e.g., '25', 'on', 'off').
        attributes: Optional dictionary of state attributes.

    Returns:
        The updated state object.

    Example:
        >>> set_state("sensor.kitchen_temperature", "25", {"unit_of_measurement": "°C"})
        {"entity_id": "sensor.kitchen_temperature", "state": "25", ...}
    """
    payload: dict[str, Any] = {"state": state}
    if attributes:
        payload["attributes"] = attributes

    response = requests.post(
        f"{_get_ha_url()}/api/states/{entity_id}",
        headers=_get_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def delete_state(entity_id: str) -> dict[str, str]:
    """Delete an entity state.

    Args:
        entity_id: The entity ID to delete.

    Returns:
        A message confirming deletion.

    Example:
        >>> delete_state("sensor.kitchen_temperature")
        {"message": "Entity sensor.kitchen_temperature deleted"}
    """
    response = requests.delete(
        f"{_get_ha_url()}/api/states/{entity_id}", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def fire_event(
    event_type: str, event_data: dict[str, Any] | None = None
) -> dict[str, str]:
    """Fire a custom event in Home Assistant.

    Args:
        event_type: The type of event to fire.
        event_data: Optional dictionary of event data.

    Returns:
        A message confirming the event was fired.

    Example:
        >>> fire_event("download_file", {"next_rising": "2016-05-31T03:39:14+00:00"})
        {"message": "Event download_file fired."}
    """
    response = requests.post(
        f"{_get_ha_url()}/api/events/{event_type}",
        headers=_get_headers(),
        json=event_data or {},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def call_service(
    domain: str,
    service: str,
    service_data: dict[str, Any] | None = None,
    return_response: bool = False,
) -> dict[str, Any]:
    """Call a service within a specific domain.

    Args:
        domain: The domain to call the service in (e.g., 'light', 'switch').
        service: The service to call (e.g., 'turn_on', 'turn_off').
        service_data: Optional dictionary of service data.
        return_response: Whether to include service response data in the result.

    Returns:
        A dictionary containing changed states and optionally service response.

    Example:
        >>> call_service("light", "turn_on", {"entity_id": "light.ceiling"})
        [{"entity_id": "light.ceiling", "state": "on", ...}]
    """
    url = f"{_get_ha_url()}/api/services/{domain}/{service}"
    if return_response:
        url += "?return_response"

    response = requests.post(
        url,
        headers=_get_headers(),
        json=service_data or {},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def render_template(template: str) -> str:
    """Render a Home Assistant template.

    Args:
        template: The Jinja2 template string to render.

    Returns:
        The rendered template as plain text.

    Example:
        >>> render_template("Paulus is at {{ states('device_tracker.paulus') }}!")
        "Paulus is at work!"
    """
    response = requests.post(
        f"{_get_ha_url()}/api/template",
        headers=_get_headers(),
        json={"template": template},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


@mcp.tool()
def get_history(
    timestamp: str | None = None,
    filter_entity_id: str | None = None,
    end_time: str | None = None,
    minimal_response: bool = False,
    no_attributes: bool = False,
    significant_changes_only: bool = False,
) -> list[list[State]]:
    """Get historical state changes for entities.

    Args:
        timestamp: Optional start timestamp (YYYY-MM-DDThh:mm:ssTZD). Defaults to 1 day ago.
        filter_entity_id: Comma-separated list of entity IDs to filter.
        end_time: Optional end timestamp for the period.
        minimal_response: Only return last_changed and state for intermediate states.
        no_attributes: Skip returning attributes from the database.
        significant_changes_only: Only return significant state changes.

    Returns:
        A list of lists of state objects, one list per entity.

    Example:
        >>> get_history(filter_entity_id="sensor.temperature")
        [[{"entity_id": "sensor.temperature", "state": "22.5", ...}, ...], ...]
    """
    params: dict[str, str] = {}
    if filter_entity_id:
        params["filter_entity_id"] = filter_entity_id
    if end_time:
        params["end_time"] = end_time
    if minimal_response:
        params["minimal_response"] = "true"
    if no_attributes:
        params["no_attributes"] = "true"
    if significant_changes_only:
        params["significant_changes_only"] = "true"

    url = f"{_get_ha_url()}/api/history/period/{timestamp or ''}"
    response = requests.get(url, headers=_get_headers(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_logbook(
    timestamp: str | None = None,
    entity: str | None = None,
    end_time: str | None = None,
) -> list[dict[str, Any]]:
    """Get logbook entries.

    Args:
        timestamp: Optional start timestamp. Defaults to 1 day ago.
        entity: Optional entity ID to filter.
        end_time: Optional end timestamp.

    Returns:
        A list of logbook entry objects.

    Example:
        >>> get_logbook()
        [{"domain": "alarm_control_panel", "message": "changed to disarmed", ...}, ...]
    """
    params: dict[str, str] = {}
    if entity:
        params["entity"] = entity
    if end_time:
        params["end_time"] = end_time

    url = f"{_get_ha_url()}/api/logbook/{timestamp or ''}"
    response = requests.get(url, headers=_get_headers(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def check_config() -> dict[str, Any]:
    """Validate configuration.yaml.

    Returns:
        A dictionary with the validation result and any errors.

    Example:
        >>> check_config()
        {"errors": null, "result": "valid"}
    """
    response = requests.post(
        f"{_get_ha_url()}/api/config/core/check_config",
        headers=_get_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def handle_intent(name: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Handle an intent.

    Args:
        name: The intent name to handle.
        data: Optional intent data.

    Returns:
        The intent handling result.

    Example:
        >>> handle_intent("SetTimer", {"seconds": "30"})
        {"speech": {"plain": {"speech": "Timer set for 30 seconds"}}, ...}
    """
    payload: dict[str, Any] = {"name": name}
    if data:
        payload["data"] = data

    response = requests.post(
        f"{_get_ha_url()}/api/intent/handle",
        headers=_get_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_error_log() -> str:
    """Get the error log from the current session.

    Returns:
        The error log as plain text.

    Example:
        >>> get_error_log()
        "15-12-20 11:02:50 homeassistant.components.recorder: Found unfinished sessions"
    """
    response = requests.get(
        f"{_get_ha_url()}/api/error_log", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.text


@mcp.tool()
def get_calendars() -> list[CalendarInfo]:
    """Get list of calendar entities.

    Returns:
        A list of calendar entity information.

    Example:
        >>> get_calendars()
        [{"entity_id": "calendar.holidays", "name": "National Holidays"}, ...]
    """
    response = requests.get(
        f"{_get_ha_url()}/api/calendars", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_calendar_events(
    calendar_entity_id: str,
    start: str | None = None,
    end: str | None = None,
) -> list[CalendarEvent]:
    """Get events from a specific calendar.

    Args:
        calendar_entity_id: The calendar entity ID (e.g., 'calendar.holidays').
        start: Optional start timestamp (ISO8601).
        end: Optional end timestamp (ISO8601).

    Returns:
        A list of calendar events.

    Example:
        >>> get_calendar_events("calendar.holidays", "2022-05-01T07:00:00.000Z", "2022-06-12T07:00:00.000Z")
        [{"summary": "Cinco de Mayo", "start": {"date": "2022-05-05"}, ...}, ...]
    """
    params: dict[str, str] = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    response = requests.get(
        f"{_get_ha_url()}/api/calendars/{calendar_entity_id}",
        headers=_get_headers(),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@mcp.resource("homeassistant://config")
def config_resource() -> dict[str, Any]:
    """Get Home Assistant configuration as a resource."""
    response = requests.get(
        f"{_get_ha_url()}/api/config", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.resource("homeassistant://states")
def states_resource() -> list[State]:
    """Get all entity states as a resource."""
    response = requests.get(
        f"{_get_ha_url()}/api/states", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.resource("homeassistant://services")
def services_resource() -> list[ServiceInfo]:
    """Get available services as a resource."""
    response = requests.get(
        f"{_get_ha_url()}/api/services", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()


@mcp.resource("homeassistant://components")
def components_resource() -> list[str]:
    """Get loaded components as a resource."""
    response = requests.get(
        f"{_get_ha_url()}/api/components", headers=_get_headers(), timeout=30
    )
    response.raise_for_status()
    return response.json()
