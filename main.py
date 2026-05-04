import requests
from bs4 import BeautifulSoup
import re
import csv
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return ""


def find_emails(html):
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return list(set(re.findall(email_pattern, html)))


def find_contact_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()

        if any(word in href for word in ["contact", "about"]):
            full_url = urljoin(base_url, href)
            links.append(full_url)

    return list(set(links))


def save_to_csv(data):
    with open("leads.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["website", "email"])

        for row in data:
            writer.writerow(row)


def main():
    url = input("Enter company website URL: ")

    all_results = []

    # 1. Главная страница
    html = get_html(url)
    emails = find_emails(html)

    for email in emails:
        all_results.append([url, email])

    # 2. Ищем contact страницы
    contact_links = find_contact_links(html, url)

    for link in contact_links:
        html = get_html(link)
        emails = find_emails(html)

        for email in emails:
            all_results.append([link, email])

    save_to_csv(all_results)

    print("Done. Found:", len(all_results), "emails")


if __name__ == "__main__":
    main()