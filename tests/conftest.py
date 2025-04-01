import pytest

@pytest.fixture
def mock_traceroute_response():
    return [
        "192.168.1.1",
        "10.0.0.1",
        "8.8.8.8"
    ]

@pytest.fixture
def mock_asn_info():
    return {
        "asn": "AS15169",
        "country": "US",
        "provider": "GOOGLE"
    }