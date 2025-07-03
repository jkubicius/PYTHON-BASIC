import importlib
from unittest.mock import patch
import pytest
res = importlib.import_module('practice.6_web_scraping.stock_info')



@pytest.fixture
def mock_get():
    with patch("requests.get") as mock:
        yield mock

def test_get_stock_codes(mock_get):
    mock_response = """
    <html>
        <table>
            <tr class="row yf-ao6als">
                <td><span class="symbol yf-hwu3c7">AAPL</span></td>
                <td><div class="leftAlignHeader companyName yf-362rys enableMaxWidth">Apple Inc.</div></td>
            </tr>
            <tr class="row yf-ao6als">
                <td><span class="symbol yf-hwu3c7">GOOGL</span></td>
                <td><div class="leftAlignHeader companyName yf-362rys enableMaxWidth">Alphabet Inc.</div></td>
            </tr>
        </table>
    </html>
    """

    mock_get.return_value.content = mock_response.encode("utf-8")
    stock_codes = res.get_stock_codes()
    assert stock_codes == {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc."
    }

def test_generate_sheet_basic():
    sheet = res.generate_sheet(
        "Dummy Sheet",
        ["Col1", "Col2"],
        [("a", "b"), ("longer", "row2")],
    )
    lines = sheet.splitlines()
    assert lines[0].startswith("=") and lines[0].endswith("=")
    assert "| Col1 " in lines[1] and "| Col2 " in lines[1]
    assert lines[-1] == ""

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("25.30%", 25.30),
        ("-3.5%", -3.5),
        ("1,234.56%", 1234.56),
        ("N/A", float("-inf")),
        (None, float("-inf")),
    ],
)
def test_parse_percent(raw, expected):
    assert res.parse_percent(raw) == expected

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("$12.5B", 12_500_000_000),
        ("$965.4M", 965_400_000),
        ("$37.2K", 37_200),
        ("12345", 12345.0),
    ],
)
def test_parse_value(raw, expected):
    assert res.parse_value(raw) == expected
