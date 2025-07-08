"""
There is a list of most active Stocks on Yahoo Finance https://finance.yahoo.com/most-active.
You need to compose several sheets based on data about companies from this list.
To fetch data from webpage you can use requests lib. To parse html you can use beautiful soup lib or lxml.
Sheets which are needed:
1. 5 stocks with most youngest CEOs and print sheet to output. You can find CEO info in Profile tab of concrete stock.
    Sheet's fields: Name, Code, Country, Employees, CEO Name, CEO Year Born.
2. 10 stocks with best 52-Week Change. 52-Week Change placed on Statistics tab.
    Sheet's fields: Name, Code, 52-Week Change, Total Cash
3. 10 largest holds of Blackrock Inc. You can find related info on the Holders tab.
    Blackrock Inc is an investment management corporation.
    Sheet's fields: Name, Code, Shares, Date Reported, % Out, Value.
    All fields except first two should be taken from Holders tab.


Example for the first sheet (you need to use same sheet format):
==================================== 5 stocks with most youngest CEOs ===================================
| Name        | Code | Country       | Employees | CEO Name                             | CEO Year Born |
---------------------------------------------------------------------------------------------------------
| Pfizer Inc. | PFE  | United States | 78500     | Dr. Albert Bourla D.V.M., DVM, Ph.D. | 1962          |
...

About sheet format:
- sheet title should be aligned to center
- all columns should be aligned to the left
- empty line after sheet

Write at least 2 tests on your choose.
Links:
    - requests docs: https://docs.python-requests.org/en/latest/
    - beautiful soup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    - lxml docs: https://lxml.de/
"""
import logging
import time
import requests
from bs4 import BeautifulSoup
import re

USER_AGENTS = ['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']

MOST_ACTIVE_STOCKS_URL = "https://finance.yahoo.com/markets/stocks/most-active"
STOCK_PROFILE_TAB_URL = "https://finance.yahoo.com/quote/{code}/profile"
STOCK_STATISTICS_TAB_URL = "https://finance.yahoo.com/quote/{code}/key-statistics"
BLK_HOLDERS_URL = "https://finance.yahoo.com/quote/BLK/holders"

class RequestRefusedException(Exception):
    pass

def make_request(url: str) -> BeautifulSoup:
    user_agent = USER_AGENTS[0]
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    try:
        time.sleep(2)
        #print(f"Using User-Agent: {user_agent}")
        response = requests.get(url, headers=headers, timeout=15)
        #print(f"Requested URL: {response.url}")
        #print(f"Status code: {response.status_code}")
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.HTTPError as e:
        raise RequestRefusedException(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise RequestRefusedException(f"Network error: {e}")


def get_stock_codes() -> dict:
    stock_codes = {}
    count = 100
    offset = 0
    rx_pages = r"^(\d+)-(\d+) of (\d+) results"

    while True:
        url = f"https://finance.yahoo.com/markets/stocks/most-active/?count={count}&start={offset}"
        soup = make_request(url)

        ticker_links = soup.find_all("a", {"data-testid": "table-cell-ticker"})
        for link in ticker_links:
            href = link.get("href", "")
            if "/quote/" in href:
                code = href.split("/quote/")[1].strip("/").split("?")[0]
                name = link.get("title", "").strip()
                if code and name:
                    stock_codes[code] = name

        result_span = soup.find("span", string=re.compile(rx_pages))
        if not result_span:
            break

        match = re.match(rx_pages, result_span.text.strip())
        if not match:
            break

        end = int(match.group(2))
        total = int(match.group(3))
        if end >= total:
            break

        offset = end
    return stock_codes

def extract_ceo_info(soup):
    try:
        table_div = soup.find("div", class_="table-container")
        if not table_div:
            return "", "N/A"

        table = table_div.find("table")
        if not table:
            return "", "N/A"

        tbody = table.find("tbody")
        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 5 and "CEO" in cells[1].text:
                name = cells[0].text.strip()
                year_text = cells[4].text.strip()
                year = int(year_text) if year_text.isdigit() else "N/A"
                return name, year
    except Exception as e:
        logging.warning(f"CEO parsing failed: {e}")
    return "", "N/A"


def get_youngest_ceos_from_profile_tab(stock_codes: dict) -> dict:
    all_data = []

    for code, name in stock_codes.items():
        soup = make_request(STOCK_PROFILE_TAB_URL.format(code=code))

        country = ""
        address_div = soup.find("div", class_="address yf-wxp4ja")
        if address_div:
            address_parts = address_div.find_all("div")
            if address_parts:
                country = address_parts[-1].text.strip()

        employees = ""
        emp_section = soup.find("dl", class_="company-stats yf-wxp4ja")
        if emp_section:
            strong = emp_section.find("strong")
            if strong:
                employees = strong.text.strip().replace(",", "")
        ceo_name, ceo_year = extract_ceo_info(soup)

        if ceo_year != "N/A":
            all_data.append({
                "Name": name,
                "Code": code,
                "Country": country,
                "Employees": employees,
                "CEO Name": ceo_name,
                "CEO Year Born": ceo_year
            })

    sorted_data = sorted(all_data, key=lambda x: x["CEO Year Born"], reverse=True)
    youngest_five = sorted_data[:5]

    stock_data = {
        "Name": [c["Name"] for c in youngest_five],
        "Code": [c["Code"] for c in youngest_five],
        "Country": [c["Country"] for c in youngest_five],
        "Employees": [c["Employees"] for c in youngest_five],
        "CEO Name": [c["CEO Name"] for c in youngest_five],
        "CEO Year Born": [c["CEO Year Born"] for c in youngest_five],
    }

    return stock_data


def parse_percent(pct_str: str) -> float:
    try:
        return float(pct_str.strip('%').replace(',', ''))
    except (AttributeError, ValueError, TypeError):
        return float('-inf')


def extract_row_value_by_label(table, expected_label: str) -> str:
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            if label.startswith(expected_label):
                return cells[1].get_text(strip=True)
    return "N/A"


def get_stocks_with_best_statistics(stock_codes: dict) -> dict:
    all_data = []
    for code, name in stock_codes.items():
        try:
            soup = make_request(STOCK_STATISTICS_TAB_URL.format(code=code))
            all_sections = soup.find_all("section", class_="yf-14j5zka")
            if len(all_sections) < 2:
                continue

            financial_highlights_section = all_sections[0]
            trading_information_section = all_sections[1]

            stock_price_history_table = trading_information_section.find("table", class_="table yf-vaowmx")
            week_52_change = extract_row_value_by_label(stock_price_history_table, "52 Week Change")

            financial_highlights_tables = financial_highlights_section.find_all("table", class_="table yf-vaowmx")
            balance_sheet_table = financial_highlights_tables[-2] if len(financial_highlights_tables) >= 2 else None
            total_cash = extract_row_value_by_label(balance_sheet_table, "Total Cash") if balance_sheet_table else "N/A"

            all_data.append({
                "Name": name,
                "Code": code,
                "52 Week Change": week_52_change,
                "Total Cash": total_cash
            })
        except Exception as e:
            logging.warning(f"Error processing {code}: {e}")

    all_data_sorted = sorted(all_data, key=lambda x: parse_percent(x["52 Week Change"]), reverse=True)
    top_ten = all_data_sorted[:10]

    return {
        "Name": [c["Name"] for c in top_ten],
        "Code": [c["Code"] for c in top_ten],
        "52 Week Change": [c["52 Week Change"] for c in top_ten],
        "Total Cash": [c["Total Cash"] for c in top_ten],
    }


def get_top_institutional_holders():
    soup = make_request(BLK_HOLDERS_URL)

    section = soup.find("section", attrs={"data-testid": "holders-top-institutional-holders"})
    if not section:
        raise ValueError("Could not find the top institutional holders section.")

    table = section.find("table")
    if not table:
        raise ValueError("Could not find the holders table.")

    tbody = table.find("tbody")
    rows = tbody.find_all("tr", class_="yf-idy1mk")

    holders = []
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 5:
            holder = columns[0].text.strip()
            shares = columns[1].text.strip()
            date_reported = columns[2].text.strip()
            percent_out = columns[3].text.strip()
            value = columns[4].text.strip()
            holders.append([holder, shares, date_reported, percent_out, value])
    return holders


def generate_sheet(title: str, headers: list[str], rows: list[list[str]]) -> str:
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    total_width = sum(col_widths) + 3 * len(headers) + 1
    sheet_lines = []

    centered_title = f" {title} ".center(total_width, "=")
    sheet_lines.append(centered_title)

    header_line = "| " + " | ".join(f"{headers[i].ljust(col_widths[i])}" for i in range(len(headers))) + " |"
    sheet_lines.append(header_line)

    sheet_lines.append("-" * len(header_line))

    for row in rows:
        row_line = "| " + " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(headers))) + " |"
        sheet_lines.append(row_line)

    sheet_lines.append("")
    return "\n".join(sheet_lines) + "\n"


def main():
    codes = get_stock_codes()

    youngest_ceos_data = get_youngest_ceos_from_profile_tab(codes)
    headers = ["Name", "Code", "Country", "Employees", "CEO Name", "CEO Year Born"]
    rows = list(zip(
        youngest_ceos_data["Name"],
        youngest_ceos_data["Code"],
        youngest_ceos_data["Country"],
        youngest_ceos_data["Employees"],
        youngest_ceos_data["CEO Name"],
        youngest_ceos_data["CEO Year Born"],
    ))
    sheet = generate_sheet("5 stocks with most youngest CEOs", headers, rows)
    print(sheet)


    best_statistics = get_stocks_with_best_statistics(codes)
    headers = ["Name", "Code", "52-Week Change", "Total Cash"]
    rows = list(zip(
        best_statistics["Name"],
        best_statistics["Code"],
        best_statistics["52 Week Change"],
        best_statistics["Total Cash"],
    ))
    sheet = generate_sheet("10 stocks with best 52-Week Change", headers, rows)
    print(sheet)


    data = get_top_institutional_holders()
    headers = ["Name", "Shares", "Date Reported", "% Out", "Value"]
    sheet = generate_sheet("10 largest holders of BlackRock Inc.", headers, data)
    print(sheet)

if __name__ == "__main__":
    main()