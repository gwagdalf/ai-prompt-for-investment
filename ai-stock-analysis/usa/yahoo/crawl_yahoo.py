import csv
import os
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

CSV_HEADER = [
    'code', 'company', 'beta',
    'Revenue(B)2024/12', 'Revenue(B)2025/12', 'Revenue(B)2026/12', 'Revenue(B)2027/12',
    'eps2024/12', 'eps2025/12', 'eps2026/12', 'eps2027/12',
    'bps2025/12', 'bps2026/12',
    'dps2024/12', 'dps2025/12', 'dps2026/12',
    '적정주가Max', '적정주가Consensus', '적정주가Min'
]


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver


def parse_value(value_str):
    """Convert Yahoo string to float. Strips B/M/T/K suffix, commas, $, %, N/A, -."""
    if not value_str:
        return 0
    s = str(value_str).strip().replace(',', '').replace('$', '').replace('%', '')
    if s in ('-', 'N/A', 'n/a', '', '--', 'NaN'):
        return 0
    for suffix in ('B', 'M', 'T', 'K'):
        if s.upper().endswith(suffix):
            s = s[:-1]
            break
    try:
        return float(s)
    except ValueError:
        return 0


def parse_revenue_b(value_str):
    """Parse revenue string like '487.04B' or '577.53M' to float in billions."""
    if not value_str:
        return 0
    s = str(value_str).strip().replace(',', '').replace('$', '')
    if s in ('-', 'N/A', 'n/a', '', '--'):
        return 0
    upper = s.upper()
    if upper.endswith('B'):
        try:
            return round(float(s[:-1]), 4)
        except ValueError:
            return 0
    if upper.endswith('M'):
        try:
            return round(float(s[:-1]) / 1000, 4)
        except ValueError:
            return 0
    if upper.endswith('T'):
        try:
            return round(float(s[:-1]) * 1000, 4)
        except ValueError:
            return 0
    try:
        return round(float(s) / 1e9, 4)
    except ValueError:
        return 0


def get_stock_data(stock_code):
    driver = setup_driver()
    results = {key: 0 for key in CSV_HEADER}
    results['code'] = stock_code
    results['company'] = 'Error'

    try:
        # === SECTION 1: financials — company name, Revenue/EPS 2024-2025 ===
        try:
            url = f"https://finance.yahoo.com/quote/{stock_code}/financials/"
            print(f"  -> financials: {url}")
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # company name: <h1 class="heading yf-ndxd9a">Apple Inc. (AAPL)</h1>
            h1 = soup.find('h1')
            if h1:
                text = h1.get_text(strip=True)
                results['company'] = text.split(' (')[0].strip() if ' (' in text else text

            # Build ordered column header list: TTM + fiscal year dates.
            # Header row on Yahoo: [Breakdown, TTM, 9/30/2025, 9/30/2024, ...]
            # get_row_values() skips the label column, so revenue_vals[0]=TTM, [1]=9/30/2025, ...
            # We must include TTM in the header list so indices stay aligned with revenue_vals.
            _date_re = re.compile(r'^\d{1,2}/\d{2}/\d{4}$')
            col_headers = []
            seen_hdrs = set()
            for div in soup.find_all('div'):
                txt = div.get_text(strip=True)
                if txt and txt not in seen_hdrs and (txt == 'TTM' or _date_re.match(txt)):
                    col_headers.append(txt)
                    seen_hdrs.add(txt)

            def find_col_index(headers, year_str):
                for i, h in enumerate(headers):
                    if year_str in h:
                        return i
                return -1

            def get_row_values(title_text):
                """Find a data row by rowTitle title attribute; return list of column text values."""
                label_div = soup.find('div', attrs={'title': title_text})
                if label_div is None:
                    for div in soup.find_all('div'):
                        if div.get_text(strip=True) == title_text:
                            label_div = div
                            break
                if label_div is None:
                    return []
                row_container = label_div
                for _ in range(5):
                    row_container = row_container.parent
                    if row_container is None:
                        break
                    cols = row_container.find_all(
                        'div', class_=lambda c: c and 'column' in c
                    )
                    if len(cols) >= 2:
                        return [c.get_text(strip=True) for c in cols[1:]]
                return []

            revenue_vals = get_row_values('Total Revenue')
            eps_vals = get_row_values('Basic EPS')

            idx_2024 = find_col_index(col_headers, '2024')
            idx_2025 = find_col_index(col_headers, '2025')

            # Financials page values are in thousands of dollars (e.g. "391,035,000" = $391B).
            # Divide parse_value() result by 1e6 to get billions.
            if idx_2024 >= 0 and idx_2024 < len(revenue_vals):
                results['Revenue(B)2024/12'] = round(parse_value(revenue_vals[idx_2024]) / 1e6, 2)
            if idx_2025 >= 0 and idx_2025 < len(revenue_vals):
                results['Revenue(B)2025/12'] = round(parse_value(revenue_vals[idx_2025]) / 1e6, 2)
            if idx_2024 >= 0 and idx_2024 < len(eps_vals):
                results['eps2024/12'] = parse_value(eps_vals[idx_2024])
            if idx_2025 >= 0 and idx_2025 < len(eps_vals):
                results['eps2025/12'] = parse_value(eps_vals[idx_2025])

        except Exception as e:
            print(f"  [WARN] financials error for {stock_code}: {e}")

        # === SECTION 2: analysis — Revenue/EPS estimates 2026-2027 ===
        try:
            url = f"https://finance.yahoo.com/quote/{stock_code}/analysis/"
            print(f"  -> analysis: {url}")
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tables = soup.find_all('table')

            def get_estimate_avg(table, col_key_0y='0y', col_key_1y='+1y'):
                """Extract Avg. Estimate for current year and next year from an estimate table."""
                if table is None:
                    return '0', '0'
                headers = table.find_all('th')
                idx_0y = -1
                idx_1y = -1
                for i, th in enumerate(headers):
                    testid = th.get('data-testid-header', '')
                    if testid == col_key_0y:
                        idx_0y = i
                    elif testid == col_key_1y:
                        idx_1y = i
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if not cells:
                        continue
                    if 'Avg. Estimate' in cells[0].get_text():
                        val_0y = cells[idx_0y].get_text(strip=True) if 0 <= idx_0y < len(cells) else '0'
                        val_1y = cells[idx_1y].get_text(strip=True) if 0 <= idx_1y < len(cells) else '0'
                        return val_0y, val_1y
                return '0', '0'

            rev_table = None
            eps_table = None

            # Distinguish Revenue Estimate table from Earnings Estimate table by heading text
            for table in tables:
                parent = table.parent
                heading_text = ''
                for _ in range(5):
                    if parent is None:
                        break
                    prev = parent.find_previous_sibling()
                    if prev:
                        heading_text = prev.get_text(strip=True).lower()
                        break
                    parent = parent.parent
                if 'revenue' in heading_text and rev_table is None:
                    rev_table = table
                elif 'earning' in heading_text and eps_table is None:
                    eps_table = table

            # fallback: first table = revenue, second = earnings
            if rev_table is None and len(tables) >= 1:
                rev_table = tables[0]
            if eps_table is None and len(tables) >= 2:
                eps_table = tables[1]

            rev_0y, rev_1y = get_estimate_avg(rev_table)
            eps_0y, eps_1y = get_estimate_avg(eps_table)

            results['Revenue(B)2026/12'] = parse_revenue_b(rev_0y)
            results['Revenue(B)2027/12'] = parse_revenue_b(rev_1y)
            results['eps2026/12'] = parse_value(eps_0y)
            results['eps2027/12'] = parse_value(eps_1y)

        except Exception as e:
            print(f"  [WARN] analysis error for {stock_code}: {e}")

        # === SECTION 3: key-statistics — BPS 2025/2026, DPS 2026 ===
        try:
            url = f"https://finance.yahoo.com/quote/{stock_code}/key-statistics/"
            print(f"  -> key-statistics: {url}")
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            pb_table = None
            pb_row = None
            for table in soup.find_all('table'):
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells and 'Price/Book' in cells[0].get_text(strip=True):
                        pb_table = table
                        pb_row = cells
                        break
                if pb_table is not None:
                    break

            if pb_row and len(pb_row) >= 2:
                results['bps2026/12'] = parse_value(pb_row[1].get_text(strip=True))

                # Read thead to find which column indices carry 2025 dates
                col_2025_indices = []
                if pb_table is not None:
                    thead = pb_table.find('thead')
                    if thead:
                        header_cells = thead.find('tr').find_all(['th', 'td'])
                        for idx, th in enumerate(header_cells[1:], start=1):
                            if '2025' in th.get_text(strip=True):
                                col_2025_indices.append(idx)

                # fallback to columns 2-5
                if not col_2025_indices:
                    col_2025_indices = list(range(2, min(6, len(pb_row))))

                quarterly_vals = []
                for idx in col_2025_indices:
                    if idx < len(pb_row):
                        v = parse_value(pb_row[idx].get_text(strip=True))
                        if v > 0:
                            quarterly_vals.append(v)
                if quarterly_vals:
                    results['bps2025/12'] = round(sum(quarterly_vals) / len(quarterly_vals), 4)

            # Forward Annual Dividend Rate → dps2026/12
            # Strategy 1: <tr> structure
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if cells and 'Forward Annual Dividend Rate' in cells[0].get_text(strip=True):
                    if len(cells) >= 2:
                        results['dps2026/12'] = parse_value(cells[1].get_text(strip=True))
                    break

            # Strategy 2: <li> structure
            if results['dps2026/12'] == 0:
                for li in soup.find_all('li'):
                    label = li.find('span', class_=lambda c: c and 'label' in c)
                    value = li.find('span', class_=lambda c: c and 'value' in c)
                    if label and value and 'Forward Annual Dividend Rate' in label.get_text(strip=True):
                        results['dps2026/12'] = parse_value(value.get_text(strip=True))
                        break

        except Exception as e:
            print(f"  [WARN] key-statistics error for {stock_code}: {e}")

        # === SECTION 4: history/dividends — DPS 2024/2025 ===
        try:
            now_ts = int(time.time())
            past_5y_ts = int((datetime.now() - timedelta(days=5 * 365)).timestamp())
            url = (
                f"https://finance.yahoo.com/quote/{stock_code}/history/"
                f"?filter=div&frequency=1mo&period1={past_5y_ts}&period2={now_ts}"
            )
            print(f"  -> history/dividends: {stock_code}")
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            yearly_dividends = {}
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) < 2:
                    continue
                date_text = cells[0].get_text(strip=True)
                event_text = cells[1].get_text(strip=True)
                if 'Dividend' not in event_text:
                    continue
                try:
                    dt = datetime.strptime(date_text, '%b %d, %Y')
                    year = dt.year
                except ValueError:
                    continue
                span = cells[1].find('span')
                amount = parse_value(span.get_text(strip=True)) if span else 0
                if amount > 0:
                    yearly_dividends[year] = round(yearly_dividends.get(year, 0) + amount, 4)

            results['dps2024/12'] = yearly_dividends.get(2024, 0)
            results['dps2025/12'] = yearly_dividends.get(2025, 0)

        except Exception as e:
            print(f"  [WARN] history error for {stock_code}: {e}")

        # === SECTION 5a: analyst-insights — Analyst Price Targets ===
        # Data lives on /analyst-insights/, NOT the main quote page.
        # Uses stable semantic classes: priceContainer + low/average/high
        try:
            url = f"https://finance.yahoo.com/quote/{stock_code}/analyst-insights/"
            print(f"  -> analyst-insights: {url}")
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            def get_price_target(semantic_class):
                div = soup.find(
                    'div',
                    class_=lambda c: c and 'priceContainer' in c and semantic_class in c
                )
                if div:
                    price_span = div.find('span', class_=lambda c: c and 'price' in c)
                    if price_span:
                        return parse_value(price_span.get_text(strip=True))
                return 0

            results['적정주가Min'] = get_price_target('low')
            results['적정주가Consensus'] = get_price_target('average')
            results['적정주가Max'] = get_price_target('high')

        except Exception as e:
            print(f"  [WARN] analyst-insights error for {stock_code}: {e}")

        # === SECTION 5b: quote main — Beta (5Y Monthly) ===
        try:
            url = f"https://finance.yahoo.com/quote/{stock_code}/"
            print(f"  -> quote main (beta): {url}")
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # <span title="Beta (5Y Monthly)"> inside <li>, sibling <span class="...value...">
            for li in soup.find_all('li'):
                label = li.find('span', attrs={'title': 'Beta (5Y Monthly)'})
                if label:
                    value_span = li.find('span', class_=lambda c: c and 'value' in c)
                    if value_span:
                        results['beta'] = parse_value(value_span.get_text(strip=True))
                    break

            if results['beta'] == 0:
                beta_label = soup.find('span', attrs={'title': 'Beta (5Y Monthly)'})
                if beta_label:
                    sib = beta_label.find_next_sibling('span')
                    if sib:
                        results['beta'] = parse_value(sib.get_text(strip=True))

            print(f"  beta={results['beta']}, "
                  f"targets Low={results['적정주가Min']} "
                  f"Avg={results['적정주가Consensus']} "
                  f"High={results['적정주가Max']}")

        except Exception as e:
            print(f"  [WARN] quote error for {stock_code}: {e}")

    except Exception as e:
        print(f"  [ERROR] {stock_code}: {e}")
    finally:
        driver.quit()

    return results


def save_to_csv(data_list):
    if not data_list:
        print("저장할 데이터가 없습니다.")
        return
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    first_data = data_list[0]
    filename = f"yahoo-{first_data['company']}포함{len(data_list)}개-{first_data['code']}-{now}.csv"
    os.makedirs('output', exist_ok=True)
    filepath = os.path.join('output', filename)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data_list)
    print(f"파일 저장 완료: {filepath}")


if __name__ == "__main__":
    STOCK_CODES = [
        "NVDA","AAPL","MSFT","AMZN","GOOGL"
        ,"AVGO","META","TSLA","MU","AMD"
        ,"ASML","INTC","CSCO","COST","LRCX"
        ,"ARM","AMAT","NFLX","PLTR","TXN"
    ]

    all_data = []
    for code in STOCK_CODES:
        print(f"데이터 수집 시작: {code}...")
        stock_data = get_stock_data(code)
        all_data.append(stock_data)

    save_to_csv(all_data)
