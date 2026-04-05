from unittest.mock import MagicMock, patch

import pytest


class TestGetApiStatus:
    def test_get_api_status_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_api_status

        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "API running."}
        mock_requests.get.return_value = mock_response

        result = get_api_status()

        assert result == {"message": "API running."}
        mock_requests.get.assert_called_once()

    def test_get_api_status_no_token(self):
        with patch.dict(
            "mcp_homeassistant._core.os.environ", {"HA_TOKEN": ""}, clear=False
        ):
            from mcp_homeassistant._core import _get_ha_token

            with pytest.raises(
                ValueError, match="HA_TOKEN environment variable is required"
            ):
                _get_ha_token()


class TestGetConfig:
    def test_get_config_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_config

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "components": ["sensor"],
            "version": "2026.4.1",
            "location_name": "Home",
        }
        mock_requests.get.return_value = mock_response

        result = get_config()

        assert result["version"] == "2026.4.1"
        assert result["location_name"] == "Home"


class TestGetStates:
    def test_get_states_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_states

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"entity_id": "sun.sun", "state": "below_horizon", "attributes": {}},
            {"entity_id": "sensor.temp", "state": "22.5", "attributes": {}},
        ]
        mock_requests.get.return_value = mock_response

        result = get_states()

        assert len(result) == 2
        assert result[0]["entity_id"] == "sun.sun"


class TestGetState:
    def test_get_state_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_state

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entity_id": "sensor.kitchen_temperature",
            "state": "22.5",
            "attributes": {"unit_of_measurement": "°C"},
        }
        mock_requests.get.return_value = mock_response

        result = get_state("sensor.kitchen_temperature")

        assert result["entity_id"] == "sensor.kitchen_temperature"
        assert result["state"] == "22.5"


class TestSetState:
    def test_set_state_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import set_state

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entity_id": "sensor.test",
            "state": "25",
            "attributes": {"unit_of_measurement": "°C"},
        }
        mock_requests.post.return_value = mock_response

        result = set_state("sensor.test", "25", {"unit_of_measurement": "°C"})

        assert result["state"] == "25"
        mock_requests.post.assert_called_once()


class TestDeleteState:
    def test_delete_state_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import delete_state

        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Entity deleted"}
        mock_requests.delete.return_value = mock_response

        result = delete_state("sensor.test")

        assert "message" in result


class TestFireEvent:
    def test_fire_event_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import fire_event

        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Event fired"}
        mock_requests.post.return_value = mock_response

        result = fire_event("custom_event", {"key": "value"})

        assert result["message"] == "Event fired"


class TestCallService:
    def test_call_service_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import call_service

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"entity_id": "light.ceiling", "state": "on", "attributes": {}}
        ]
        mock_requests.post.return_value = mock_response

        result = call_service("light", "turn_on", {"entity_id": "light.ceiling"})

        assert len(result) > 0


class TestRenderTemplate:
    def test_render_template_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import render_template

        mock_response = MagicMock()
        mock_response.text = "Paulus is at work!"
        mock_response.json.return_value = mock_response.text
        mock_requests.post.return_value = mock_response

        result = render_template("Paulus is at {{ states('device_tracker.paulus') }}!")

        assert result == "Paulus is at work!"


class TestGetHistory:
    def test_get_history_with_entity_filter(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_history

        mock_response = MagicMock()
        mock_response.json.return_value = [
            [
                {
                    "entity_id": "sensor.temperature",
                    "state": "22.5",
                    "attributes": {},
                    "last_changed": "2026-04-01T12:00:00Z",
                    "last_updated": "2026-04-01T12:00:00Z",
                }
            ]
        ]
        mock_requests.get.return_value = mock_response

        result = get_history(filter_entity_id="sensor.temperature")

        assert len(result) > 0


class TestGetLogbook:
    def test_get_logbook_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_logbook

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "domain": "alarm_control_panel",
                "entity_id": "alarm_control_panel.area_001",
                "message": "changed to disarmed",
            }
        ]
        mock_requests.get.return_value = mock_response

        result = get_logbook()

        assert len(result) > 0


class TestCheckConfig:
    def test_check_config_valid(self, mock_requests, mock_env):
        from mcp_homeassistant._core import check_config

        mock_response = MagicMock()
        mock_response.json.return_value = {"errors": None, "result": "valid"}
        mock_requests.post.return_value = mock_response

        result = check_config()

        assert result["result"] == "valid"


class TestHandleIntent:
    def test_handle_intent_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import handle_intent

        mock_response = MagicMock()
        mock_response.json.return_value = {"speech": {"plain": {"speech": "Timer set"}}}
        mock_requests.post.return_value = mock_response

        result = handle_intent("SetTimer", {"seconds": "30"})

        assert "speech" in result


class TestGetErrorLog:
    def test_get_error_log_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_error_log

        mock_response = MagicMock()
        mock_response.text = "Error log content"
        mock_requests.get.return_value = mock_response

        result = get_error_log()

        assert result == "Error log content"


class TestGetCalendars:
    def test_get_calendars_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_calendars

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"entity_id": "calendar.holidays", "name": "National Holidays"}
        ]
        mock_requests.get.return_value = mock_response

        result = get_calendars()

        assert len(result) > 0
        assert result[0]["entity_id"] == "calendar.holidays"


class TestGetCalendarEvents:
    def test_get_calendar_events_success(self, mock_requests, mock_env):
        from mcp_homeassistant._core import get_calendar_events

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "summary": "Cinco de Mayo",
                "start": {"date": "2022-05-05"},
                "end": {"date": "2022-05-06"},
            }
        ]
        mock_requests.get.return_value = mock_response

        result = get_calendar_events("calendar.holidays", "2022-05-01", "2022-06-01")

        assert len(result) > 0
        assert result[0]["summary"] == "Cinco de Mayo"
