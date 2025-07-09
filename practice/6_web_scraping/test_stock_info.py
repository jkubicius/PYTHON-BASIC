import importlib
res = importlib.import_module('practice.6_web_scraping.stock_info')
import stock_info
import pytest


def test_parse_percent_various():
    assert stock_info.parse_percent('12.34%') == pytest.approx(12.34)
    assert stock_info.parse_percent('1,234.56%') == pytest.approx(1234.56)
    assert stock_info.parse_percent('invalid%') == 0.0

def test_parse_shares_various():
    assert stock_info.parse_shares('10K') == pytest.approx(10_000)
    assert stock_info.parse_shares('2.5M') == pytest.approx(2_500_000)
    assert stock_info.parse_shares('100') == pytest.approx(100)
    assert stock_info.parse_shares('invalid') == pytest.approx(0.0)

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

