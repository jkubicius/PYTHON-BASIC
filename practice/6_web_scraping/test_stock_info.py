import importlib
from unittest.mock import patch
from bs4 import BeautifulSoup
res = importlib.import_module('practice.6_web_scraping.stock_info')


@patch.object(res, "make_request")
def test_get_stock_codes(mock_make_request):
    html = """
    <html>
        <a href="/quote/AAPL" title="Apple Inc." data-testid="table-cell-ticker">AAPL</a>
        <a href="/quote/GOOGL" title="Alphabet Inc." data-testid="table-cell-ticker">GOOGL</a>
        <span>1-100 of 100 results</span>
    </html>
    """
    mock_soup = BeautifulSoup(html, "html.parser")
    mock_make_request.return_value = mock_soup

    stock_codes = res.get_stock_codes()
    assert stock_codes == {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc."
    }


def test_generate_sheet():
    title = "5 stocks with most youngest CEOs"
    headers = ["Name", "Code", "Country", "Employees", "CEO Name", "CEO Year Born"]
    rows = [["Pfizer Inc.", "PFE", "United States", "78500", "Dr. Albert Bourla D.V.M., DVM, Ph.D.", "1962"]]

    expected_output = """==================================== 5 stocks with most youngest CEOs ===================================
| Name        | Code | Country       | Employees | CEO Name                             | CEO Year Born |
---------------------------------------------------------------------------------------------------------
| Pfizer Inc. | PFE  | United States | 78500     | Dr. Albert Bourla D.V.M., DVM, Ph.D. | 1962          |

"""
    output = res.generate_sheet(title, headers, rows)
    assert output == expected_output

