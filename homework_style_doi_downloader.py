# -*- coding: utf-8 -*-
"""
Homework-style DOI downloader template.

This file is written in the same simple style as the example:
    1. read doi.txt
    2. build one URL for each DOI
    3. request the URL
    4. save PDF into downloadArticles/
    5. write failed DOI values into error.txt

Use only with an address/service you are authorized to use.
The address should return a PDF directly, or redirect to a PDF.
"""

import os
import webbrowser
import time
import random
from urllib.parse import quote, urljoin

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError(
        "This script needs BeautifulSoup. Install it with: python3 -m pip install beautifulsoup4"
    )


# ============================================================
# 1. Put your authorized address here
# ============================================================
# You have two choices:
#
# Choice A: base address; the DOI from doi.txt will be added after it.
# Example:
# BASE_URL = "https://your-authorized-address.example/"
#
# Choice B: address with {doi}; the DOI from doi.txt will replace {doi}.
# Example:
# BASE_URL = "https://your-authorized-address.example/pdf?doi={doi}"
#
# Do not type the DOI here. DOI values are read from doi.txt below.
BASE_URL = "https://sci-hub.sidesgame.com/"

# Open legal DOI landing pages in browser tabs for cases where
# the script found a PDF URL but could not download it.
# This helps manual retrieval through authorized/library access.
OPEN_DOI_TABS_FOR_MANUAL_DOWNLOAD = True
DOI_LANDING_BASE = "https://doi.org/"

# Pause between articles: 10-20 seconds, plus 0-30% extra.
# HTTP 429 can still require a longer server-directed wait.
REQUEST_DELAY_MIN_SECONDS = 10
REQUEST_DELAY_MAX_SECONDS = 20
REQUEST_DELAY_EXTRA_FRACTION = 0.30


# ============================================================
# 2. Prepare folder and files
# ============================================================
path = "./downloadArticles/"

if os.path.exists(path) == False:
    os.mkdir(path)

f = open("doi.txt", "r", encoding="utf-8")

head = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/pdf,*/*;q=0.8",
}


# ============================================================
# 3. Helper functions
# ============================================================
def next_article_delay():
    """Return a randomized pause of 10 to 26 seconds with default settings."""
    base = random.uniform(REQUEST_DELAY_MIN_SECONDS, REQUEST_DELAY_MAX_SECONDS)
    return base * (1 + random.uniform(0, REQUEST_DELAY_EXTRA_FRACTION))


def make_url(base_url, doi):
    """Create the request URL for one DOI."""
    if base_url == "":
        raise ValueError("Please put your authorized address into BASE_URL.")

    doi_for_url = requests.utils.quote(doi, safe="")

    if "{doi}" in base_url:
        return base_url.replace("{doi}", doi_for_url)

    if base_url.endswith("/"):
        return base_url + doi_for_url

    return base_url + "/" + doi_for_url


def make_pdf_name(doi):
    """Change DOI into a filename-safe PDF name."""
    return doi.replace("/", "_").replace(":", "_") + ".pdf"


def explain_error(step, error_message):
    """Give student-friendly advice based on the failed step."""
    advice = {
        "SETUP": (
            "Check BASE_URL near the top of the script. It cannot be empty. "
            "Use either a base address ending with / or an address containing {doi}."
        ),
        "REQUEST_FIRST_URL": (
            "The program could not open the first URL. Check whether BASE_URL is correct, "
            "whether the internet works, and whether the website is reachable in a browser."
        ),
        "PARSE_HTML": (
            "The first URL returned a webpage, but the program could not find a PDF link. "
            "Open the printed request URL in a browser, inspect where the PDF button/link is, "
            "then add a new parsing rule inside find_pdf_url_in_html()."
        ),
        "REQUEST_PDF_URL": (
            "The program found a possible PDF URL, but could not download it. "
            "Open the printed PDF URL in a browser. It may require login, cookies, or manual access."
        ),
        "CHECK_PDF": (
            "The response was not a real PDF file. The website may have returned an HTML login page, "
            "an error page, or a JavaScript viewer instead of PDF bytes."
        ),
        "SAVE_FILE": (
            "The PDF was downloaded but could not be saved. Check folder permissions and filename/path."
        ),
    }

    return advice.get(step, "Read the error message and check the URL manually.") + "\nOriginal error: " + str(error_message)


def find_pdf_url_in_html(html_text, page_url):
    """
    Find a PDF URL inside a normal HTML webpage.

    This demonstrates the important second step:
        landing page HTML -> parse HTML -> find PDF link

    Different websites write PDF links differently, so we check several
    common patterns:
        1. <meta name="citation_pdf_url" content="...">
        2. <a href="...pdf">PDF</a>
        3. <iframe src="...pdf">
        4. <embed src="...pdf">
    """
    soup = BeautifulSoup(html_text, "html.parser")

    # Pattern 1: citation metadata commonly used by journal pages.
    meta_pdf = soup.find("meta", attrs={"name": "citation_pdf_url"})
    if meta_pdf is not None and meta_pdf.get("content"):
        return urljoin(page_url, meta_pdf.get("content"))

    # Pattern 2: ordinary PDF hyperlink.
    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.get_text(" ", strip=True).lower()
        if href and (".pdf" in href.lower() or "pdf" in text):
            return urljoin(page_url, href)

    # Pattern 3: PDF shown inside an iframe.
    iframe = soup.find("iframe")
    if iframe is not None and iframe.get("src"):
        src = iframe.get("src")
        if ".pdf" in src.lower() or "pdf" in src.lower():
            return urljoin(page_url, src)

    # Pattern 4: PDF shown inside an embed tag.
    embed = soup.find("embed")
    if embed is not None and embed.get("src"):
        src = embed.get("src")
        if ".pdf" in src.lower() or "pdf" in src.lower():
            return urljoin(page_url, src)

    raise ValueError("The page is HTML, but no PDF link was found inside it.")


# ============================================================
# 4. Download each DOI
# ============================================================
session = requests.Session()
session.headers.update(head)

final_errors = []
manual_open_items = []
no_pdf_link_items = []

first_request = True

for line in f.readlines():
    line = line.strip()

    if line == "":
        continue

    existing_path = path + make_pdf_name(line)
    if os.path.isfile(existing_path):
        with open(existing_path, "rb") as existing:
            if existing.read(5) == b"%PDF-":
                print(line + " already has a PDF; skipping.")
                continue

    if not first_request:
        delay = next_article_delay()
        print("--Waiting {:.1f} seconds before the next article...".format(delay))
        time.sleep(delay)
    first_request = False

    download_url = ""
    failed_step = ""

    try:
        failed_step = "SETUP"
        url = make_url(BASE_URL, line)

        print(line + " is downloading...")
        print("--The request url is: " + url)

        failed_step = "REQUEST_FIRST_URL"
        # Step 1: request the DOI/resolver/landing-page URL.
        r = session.get(url, timeout=45, allow_redirects=True)
        r.raise_for_status()
        download_url = r.url

        # Step 2A: if the first response is already a PDF, save it directly.
        if r.content.startswith(b"%PDF"):
            pdf_content = r.content

        # Step 2B: if the first response is HTML, parse the page and find
        # the real PDF URL, then request that second URL.
        else:
            print("--The first response is not a PDF; parsing HTML page...")
            failed_step = "PARSE_HTML"
            download_url = find_pdf_url_in_html(r.text, r.url)
            print("--The PDF url found in HTML is: " + download_url)

            failed_step = "REQUEST_PDF_URL"
            # Preserve the landing-page session and identify the referring article.
            download_r = session.get(download_url, headers={"Referer": r.url}, timeout=45, allow_redirects=True)
            download_r.raise_for_status()

            failed_step = "CHECK_PDF"
            if not download_r.content.startswith(b"%PDF"):
                content_type = download_r.headers.get("Content-Type", "")
                raise ValueError(
                    "The second response is still not a PDF. "
                    + "Content-Type: "
                    + content_type
                    + "; final URL: "
                    + download_r.url
                )

            pdf_content = download_r.content

        pdf_name = make_pdf_name(line)
        pdf_path = path + pdf_name

        failed_step = "SAVE_FILE"
        with open(pdf_path, "wb+") as temp:
            temp.write(pdf_content)

        print(line + " download successfully.\n")

    except Exception as e:
        student_message = explain_error(failed_step, e)
        error_item = {
            "doi": line,
            "pdf_name": make_pdf_name(line),
            "failed_step": failed_step,
            "reason": str(e),
            "student_message": student_message,
            "final_url": download_url,
        }
        final_errors.append(error_item)

        # Alternative manual workflow:
        # REQUEST_PDF_URL means the HTML page exposed a PDF link, but requests
        # could not fetch the PDF. Open the DOI landing page instead of the
        # blocked PDF/mirror URL so the user can retrieve it through authorized
        # browser/library access.
        if failed_step in ("REQUEST_PDF_URL", "REQUEST_FIRST_URL", "PARSE_HTML", "CHECK_PDF"):
            doi_url = DOI_LANDING_BASE + quote(line, safe="/")
            manual_open_items.append({
                "doi": line,
                "doi_url": doi_url,
                "blocked_pdf_url_recorded_for_debug_only": download_url,
            })
            if OPEN_DOI_TABS_FOR_MANUAL_DOWNLOAD:
                try:
                    opened = webbrowser.open_new_tab(doi_url)
                    if not opened:
                        print("--Open this DOI page manually: " + doi_url)
                except Exception:
                    print("--Open this DOI page manually: " + doi_url)

        # PARSE_HTML means no PDF link was discovered in the HTML. Keep these
        # in a separate DOI list for later searching.
        if failed_step == "PARSE_HTML":
            no_pdf_link_items.append(error_item)

        print(line + " occurs error.\n")
        print("--Failed step: " + failed_step)
        print("--What to do: " + student_message + "\n")


f.close()


# ============================================================
# 5. Write final error.txt only after validating downloaded files
# ============================================================
# error.txt only contains DOI values, one DOI per line.
# error_details.txt contains the teaching/debugging explanation.
with open("error.txt", "w", encoding="utf-8") as error, open("error_details.txt", "w", encoding="utf-8") as details:
    missing_count = 0

    for item in final_errors:
        expected_pdf = path + item["pdf_name"]

        # Final validation:
        # If the expected PDF exists and has content, do not write it to error.txt.
        # This prevents error.txt from keeping old/intermediate errors after a retry succeeds.
        if os.path.exists(expected_pdf):
            with open(expected_pdf, "rb") as existing:
                if existing.read(5) == b"%PDF-":
                    continue

        missing_count = missing_count + 1
        error.write(item["doi"] + "\n")

        details.write(item["doi"] + " was NOT downloaded.\n")
        details.write("--Expected PDF file: " + expected_pdf + "\n")
        details.write("--Failed step: " + item["failed_step"] + "\n")
        details.write("--Reason: " + item["reason"] + "\n")
        details.write("--What to do: " + item["student_message"] + "\n")
        if item["final_url"] != "":
            details.write("--The final url is: " + item["final_url"] + "\n")
        details.write("\n")

# ============================================================
# 6. Write alternative manual-retrieval files
# ============================================================
with open("manual_open_doi_urls.txt", "w", encoding="utf-8") as manual_urls, \
     open("manual_open_doi_list.txt", "w", encoding="utf-8") as manual_dois:
    for item in manual_open_items:
        manual_dois.write(item["doi"] + "\n")
        manual_urls.write(item["doi"] + "\t" + item["doi_url"] + "\n")

with open("doi_no_pdf_link_remaining.txt", "w", encoding="utf-8") as no_pdf_file:
    for item in no_pdf_link_items:
        no_pdf_file.write(item["doi"] + "\n")

print("Final validation finished.")
print("Only DOIs without a PDF file are listed in error.txt.")
print("Detailed explanations are listed in error_details.txt.")
print("DOI landing pages for manual browser retrieval are listed in manual_open_doi_urls.txt.")
print("DOIs with no PDF link found in HTML are listed in doi_no_pdf_link_remaining.txt.")
