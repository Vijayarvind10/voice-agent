import sys
import pytest
from unittest.mock import MagicMock

# Mock fastapi and uvicorn before importing server
# This is necessary because the environment might not have these installed
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Now import the function to test
from server import classify

def test_classify_timer_slot_filling_duration():
    """Test slot filling when awaiting timer duration with explicit units."""
    session_state = {"awaiting_slot": "timer_duration"}
    result = classify("10 minutes", session_state)
    assert result["intent"] == "SET_TIMER"
    assert result["params"]["seconds"] == 600
    assert result["params"]["duration"] == "10 minutes"

def test_classify_timer_slot_filling_numeric():
    """Test slot filling when awaiting timer duration with just a number."""
    session_state = {"awaiting_slot": "timer_duration"}
    result = classify("10", session_state)
    assert result["intent"] == "SET_TIMER"
    assert result["params"]["seconds"] == 600
    assert "minutes" in result["params"]["duration"]

def test_classify_timer_slot_filling_cancel():
    """Test falling through when awaiting slot but user changes subject."""
    session_state = {"awaiting_slot": "timer_duration"}
    # User says something unrelated to duration
    result = classify("what is the weather", session_state)
    # Should be classified as weather
    assert result["intent"] == "GET_WEATHER"

def test_classify_repeat_last():
    assert classify("repeat command")["intent"] == "REPEAT_LAST"
    assert classify("do that again")["intent"] == "REPEAT_LAST"

def test_classify_recall_history():
    assert classify("what did i say")["intent"] == "RECALL_HISTORY"
    assert classify("show history")["intent"] == "RECALL_HISTORY"

def test_classify_set_timer_with_duration():
    result = classify("set a timer for 5 minutes")
    assert result["intent"] == "SET_TIMER"
    assert result["params"]["seconds"] == 300

def test_classify_set_timer_missing_slot():
    result = classify("set a timer")
    assert result["intent"] == "MISSING_SLOT"
    assert result["params"]["slot"] == "timer_duration"

def test_classify_play_music():
    result = classify("play jazz music")
    assert result["intent"] == "PLAY_MUSIC"
    # "music" is not removed from the query, only "play" is.
    assert "jazz" in result["params"]["query"]

def test_classify_get_weather():
    result = classify("weather in London")
    assert result["intent"] == "GET_WEATHER"
    # Input is converted to lowercase in classify()
    assert result["params"]["location"] == "london"

    result = classify("what is the weather")
    assert result["intent"] == "GET_WEATHER"

def test_classify_take_screenshot():
    assert classify("take a screenshot")["intent"] == "TAKE_SCREENSHOT"

def test_classify_clipboard():
    assert classify("show clipboard")["intent"] == "CLIPBOARD"
    assert classify("paste")["intent"] == "CLIPBOARD"

def test_classify_system_info():
    assert classify("battery status")["intent"] == "SYSTEM_INFO"
    assert classify("cpu usage")["intent"] == "SYSTEM_INFO"

def test_classify_volume_control():
    assert classify("mute volume")["intent"] == "VOLUME_CONTROL"
    assert classify("unmute")["intent"] == "VOLUME_CONTROL"

    result = classify("set volume to 50")
    assert result["intent"] == "VOLUME_CONTROL"
    assert result["params"]["level"] == 50

def test_classify_create_note():
    result = classify("create a note buy milk")
    assert result["intent"] == "CREATE_NOTE"
    assert "buy milk" in result["params"]["body"]

def test_classify_create_reminder():
    result = classify("remind me to call mom")
    assert result["intent"] == "CREATE_REMINDER"
    assert "call mom" in result["params"]["body"]

def test_classify_open_finder():
    result = classify("open downloads folder")
    assert result["intent"] == "OPEN_FINDER"
    assert result["params"]["folder"] == "downloads"

def test_classify_followup_message():
    # Requires both message and follow-up keywords
    assert classify("follow up message")["intent"] == "FOLLOWUP_FROM_MESSAGE"

def test_classify_web_search():
    result = classify("search for funny cats")
    assert result["intent"] == "WEB_SEARCH"
    assert result["params"]["query"] == "funny cats"

def test_classify_open_maps():
    result = classify("open maps to Paris")
    assert result["intent"] == "OPEN_MAPS"
    assert "paris" in result["params"]["query"]

def test_classify_send_message():
    assert classify("send a message")["intent"] == "SEND_MESSAGE"

def test_classify_create_event():
    assert classify("create a new event")["intent"] == "CREATE_EVENT"

def test_classify_open_app():
    result = classify("open calculator")
    assert result["intent"] == "OPEN_APP"
    assert result["params"]["app"] == "calculator"

def test_classify_get_date_time():
    assert classify("what time is it")["intent"] == "GET_DATE_TIME"
    assert classify("what's the date")["intent"] == "GET_DATE_TIME"

def test_classify_calculate():
    result = classify("calculate 5 plus 5")
    assert result["intent"] == "CALCULATE"
    assert "5 plus 5" in result["params"]["expression"]

def test_classify_tell_joke():
    assert classify("tell me a joke")["intent"] == "TELL_JOKE"

def test_classify_get_quote():
    assert classify("give me a quote")["intent"] == "GET_QUOTE"

def test_classify_flip_coin():
    assert classify("flip a coin")["intent"] == "FLIP_COIN"

def test_classify_roll_die():
    assert classify("roll a die")["intent"] == "ROLL_DIE"

def test_classify_define_word():
    result = classify("define algorithm")
    assert result["intent"] == "DEFINE_WORD"
    assert result["params"]["word"] == "algorithm"

def test_classify_convert_currency():
    assert classify("convert usd to eur")["intent"] == "CONVERT_CURRENCY"

def test_classify_get_ip():
    assert classify("what is my ip")["intent"] == "GET_IP"

def test_classify_get_uptime():
    assert classify("system uptime")["intent"] == "GET_UPTIME"

def test_classify_unsupported():
    result = classify("xyz123 random text")
    assert result["intent"] == "UNSUPPORTED"
    assert result["supported"] is False

def test_classify_case_insensitive():
    assert classify("SET A TIMER FOR 5 MINUTES")["intent"] == "SET_TIMER"
    assert classify("WeAtHeR iN PaRiS")["intent"] == "GET_WEATHER"
