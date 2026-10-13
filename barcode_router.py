
from urllib.parse import urlparse
from uuid import UUID


def route_barcode(barcode_text, barcode_format):
    # Reject unexpected input types
    if not isinstance(barcode_text, str) or not isinstance(barcode_format, str):
        return "unknown"

    # Parse the barcode as a URL
    try:
        parsed = urlparse(barcode_text)
    except ValueError:
        return "unknown"

    # Check the expected HomeBox URL structure
    if (
        parsed.path.startswith("/location/")
        and parsed.scheme == "https"
        and parsed.netloc == "homebox.bluflixplus.xyz"
        and parsed.query == ""
        and parsed.fragment == ""
    ):
        parts = parsed.path.split("/")

        if len(parts) != 3:
            return "unknown"

        identifier_text = parts[2]

        # Validate the location UUID
        try:
            identifier = UUID(identifier_text)
        except ValueError:
            return "unknown"

        # Require the canonical UUID representation
        if str(identifier) != identifier_text:
            return "unknown"

        # Require an exact match to the expected URL
        expected_url = f"https://homebox.bluflixplus.xyz/location/{identifier}"

        if barcode_text == expected_url:
            return "homebox_location"

    return "unknown"


if __name__ == "__main__":
    test_url = "https://homebox.bluflixplus.xyz/location/326ba7f5-0c95-4ae9-afc6-fb5a13bb1222"

    result = route_barcode(test_url, "QR Code")
    print(result)
