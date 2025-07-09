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
        print(f"Using User-Agent: {user_agent}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Requested URL: {response.url}")
        print(f"Status code: {response.status_code}")
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.HTTPError as e:
        raise RequestRefusedException(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise RequestRefusedException(f"Network error: {e}")


def get_stock_codes_from_page(soup: BeautifulSoup) -> dict:
    rows = soup.find_all("tr", class_="row yf-ao6als")
    stock_codes = {}

    for row in rows:
        code_element = row.find("span", class_="symbol yf-90gdtp")
        company_element = row.find("div", class_="leftAlignHeader companyName yf-362rys enableMaxWidth")

        if code_element and company_element:
            stock_codes[code_element.text.strip()] = company_element.text.strip()

    return stock_codes

def get_stock_codes() -> dict:
    all_stocks = {}
    start = 0
    count = 200

    while True:
        url = f"{MOST_ACTIVE_STOCKS_URL}?start={start}&count={count}"
        logging.info(f"Fetching page (start={start}, count={count})")

        try:
            soup = make_request(url)
            page_stocks = get_stock_codes_from_page(soup)

            if not page_stocks:
                logging.info("No more stocks found. Stopping.")
                break

            logging.info(f"Found {len(page_stocks)} stocks on page")
            all_stocks.update(page_stocks)

            if len(page_stocks) < count:
                logging.info("Reached end of available stocks.")
                break

            start += count

        except RequestRefusedException as e:
            logging.error(f"Request failed: {e}")
            break

    logging.info(f"Total stocks collected: {len(all_stocks)}")
    return all_stocks


def parse_profile_country(soup: BeautifulSoup) -> str:
    address_div = soup.find("div", class_="address yf-wxp4ja")
    if not address_div:
        return "N/A"
    lines = [div.get_text(strip=True) for div in address_div.find_all("div")]
    return lines[-1] if lines else "N/A"


def parse_profile_employees(soup: BeautifulSoup) -> str:
    emp_section = soup.find("dl", class_="company-stats yf-wxp4ja")
    if not emp_section:
        return "N/A"
    strong = emp_section.find("strong")
    if not strong:
        return "N/A"
    return strong.get_text(strip=True).replace(',', '')


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


def get_youngest_ceos_from_profile_tab(stock_codes: dict[str, str]) -> list[dict]:
    data: list[dict] = []

    for code, name in stock_codes.items():
        soup = make_request(f"https://finance.yahoo.com/quote/{code}/profile")

        country   = parse_profile_country(soup)
        employees = parse_profile_employees(soup)
        ceo_name, ceo_year = extract_ceo_info(soup)

        if isinstance(ceo_year, int):
            data.append({
                "Name":           name,
                "Code":           code,
                "Country":        country,
                "Employees":      employees,
                "CEO Name":       ceo_name,
                "CEO Year Born":  ceo_year
            })

    sorted_data = sorted(data, key=lambda x: x["CEO Year Born"], reverse=True)
    return sorted_data[:5]


def parse_percent(pct_str: str) -> float:
    try:
        return float(pct_str.strip('%').replace(',', ''))
    except ValueError:
        return 0.0


def extract_row_value_by_label(table, expected_label: str) -> str:
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            if label.startswith(expected_label):
                return cells[1].get_text(strip=True)
    return "N/A"


def get_top_52week_stats(stock_codes: dict[str, str]) -> list[dict]:
    data: list[dict] = []

    for code, name in stock_codes.items():
        try:
            soup = make_request(f"https://finance.yahoo.com/quote/{code}/key-statistics")
            sections = soup.find_all("section", class_="yf-14j5zka")
            if len(sections) < 2:
                continue

            trading_sec = sections[1]
            tbl = trading_sec.find("table", class_="table yf-vaowmx")
            change_52 = extract_row_value_by_label(tbl, "52 Week Change")

            fin_sec = sections[0]
            tables = fin_sec.find_all("table", class_="table yf-vaowmx")
            bs_tbl = tables[-2] if len(tables) >= 2 else None
            total_cash = extract_row_value_by_label(bs_tbl, "Total Cash") if bs_tbl else "N/A"

            data.append({
                "Name": name,
                "Code": code,
                "52-Week Change": change_52,
                "Total Cash": total_cash
            })
        except Exception:
            continue

    sorted_data = sorted(
        data,
        key=lambda x: parse_percent(x["52-Week Change"]),
        reverse=True
    )
    return sorted_data[:10]


def parse_shares(shares_str: str) -> float:
    s = shares_str.strip().upper().replace(',', '')
    mult = {'K': 1e3, 'M': 1e6, 'B': 1e9}
    if s and s[-1] in mult:
        return float(s[:-1]) * mult[s[-1]]
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_value(value_str: str) -> int:
    return int(value_str.replace(',', '').strip())


def get_top_institutional_holders() -> list[list[str]]:
    soup    = make_request(BLK_HOLDERS_URL)
    section = soup.find("section", {"data-testid": "holders-top-institutional-holders"})
    table   = section.find("table")
    rows    = table.find("tbody").find_all("tr")

    holders = []
    for tr in rows:
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) < 5:
            continue
        name, shares_raw, date_rep, pct_raw, value_raw = cols[:5]

        shares_num = parse_shares(shares_raw)
        pct_num    = parse_percent(pct_raw)
        value_num  = parse_value(value_raw)

        holders.append((value_num, [
            name,
            shares_num,
            date_rep,
            pct_num,
            value_raw
        ]))

    top10 = sorted(holders, key=lambda x: x[0], reverse=True)[:10]

    return [entry[1] for entry in top10]


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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    codes = get_stock_codes()

    youngest_ceos = get_youngest_ceos_from_profile_tab(codes)
    headers_ceo = ["Name", "Code", "Country", "Employees", "CEO Name", "CEO Year Born"]
    rows_ceo = [[item[h] for h in headers_ceo] for item in youngest_ceos]
    print(generate_sheet("5 stocks with most youngest CEOs", headers_ceo, rows_ceo))

    top_stats = get_top_52week_stats(codes)
    headers_stats = ["Name", "Code", "52-Week Change", "Total Cash"]
    rows_stats = [[item[h] for h in headers_stats] for item in top_stats]
    print(generate_sheet("10 stocks with best 52-Week Change", headers_stats, rows_stats))

    holders_rows = get_top_institutional_holders()
    print(generate_sheet(
        "10 largest holds of BlackRock Inc.",
        ["Name", "Shares", "Date Reported", "% Out", "Value"],
        holders_rows
    ))

if __name__ == "__main__":
    main()