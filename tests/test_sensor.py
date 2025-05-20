import pytest
from custom_components.smartdaily_postal_ha.sensor import PackageTrackerSensor

def make_sensor():
    # 建立一個最小化的 sensor 實例
    return PackageTrackerSensor("test_device", "test_com")

def test_parse_time_just_now():
    sensor = make_sensor()
    result = sensor.parse_time("剛剛")
    assert result is not None
    assert len(result) == 16  # 格式 yyyy/MM/dd HH:MM

def test_parse_time_yesterday():
    sensor = make_sensor()
    result = sensor.parse_time("昨天 12:34")
    assert result is not None
    assert len(result) == 16

def test_parse_time_hours_ago():
    sensor = make_sensor()
    result = sensor.parse_time("2小時以前")
    assert result is not None
    assert len(result) == 16

def test_parse_time_minutes_ago():
    sensor = make_sensor()
    result = sensor.parse_time("15分鐘以前")
    assert result is not None
    assert len(result) == 16

def test_parse_time_standard():
    sensor = make_sensor()
    # 測試標準格式（假設為 UTC 時間）
    result = sensor.parse_time("2024/05/20 10:00")
    assert result is not None
    assert len(result) == 16

def test_sensor_init():
    sensor = make_sensor()
    assert sensor._name == "My Package Tracker"
    assert sensor._com_id == "test_com"
    assert sensor._device_id == "test_device"
