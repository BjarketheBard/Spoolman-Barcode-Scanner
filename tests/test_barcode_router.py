
import pytest
from barcode_router import route_barcode


def test_valid_homebox_location():
    url = "https://homebox.bluflixplus.xyz/location/326ba7f5-0c95-4ae9-afc6-fb5a13bb1222"

    result = route_barcode(url, "QR Code")

    assert result == "homebox_location"


def test_invalid_homebox_uuid():
    url = "https://homebox.bluflixplus.xyz/location/banana"

    result = route_barcode(url, "QR Code")

    assert result == "unknown"


@pytest.mark.parametrize("barcode, expected", [
    (
        "https://homebox.bluflixplus.xyz/settings",
        "unknown"
    ),
    (
        "https://homebox.bluflixplus.xyz/location/banana",
        "unknown"
    ),
    (
        "https://homebox.bluflixplus.xyz:9999/location/326ba7f5-0c95-4ae9-afc6-fb5a13bb1222",
        "unknown"
    ),
    (
        "https://homebox.bluflixplus.xyz/location/326BA7F5-0C95-4AE9-AFC6-FB5A13BB1222",
        "unknown"
    ),
    (
        "https://homebox.bluflixplus.xyz/location/326ba7f5-0c95-4ae9-afc6-fb5a13bb1222/extra",
        "unknown"
    ),
])
def test_invalid_homebox_urls(barcode, expected):
    result = route_barcode(barcode, "QR Code")

    assert result == expected


def test_none_barcode():
    result = route_barcode(None, "QR Code")

    assert result == "unknown"


@pytest.mark.parametrize("barcode, barcode_format", [
    (
        "",
        "QR Code"
    ),
    (
        12345,
        "EAN-13"
    ),
    (
        "https://[",
        "QR Code"
    ),
    (
        "https://homebox.bluflixplus.xyz/location/326ba7f5-0c95-4ae9-afc6-fb5a13bb1222",
        None
    ),
])
def test_invalid_barcode_inputs(barcode, barcode_format):
    result = route_barcode(barcode, barcode_format)

    assert result == "unknown"
