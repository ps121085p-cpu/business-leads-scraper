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
    except Exception as error:
        print("Error loading page:", error)
        return ""


def find_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}"
    raw_emails = re.findall(email_pattern, text)

    return list(set(email.strip() for email in raw_emails))


def find_phones(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    phone_pattern = r"\+?\d[\d\s().-]{8,20}\d"
    raw_phones = re.findall(phone_pattern, text)

    cleaned_phones = []

    for phone in raw_phones:
        digits = re.sub(r"\D", "", phone)

        if 10 <= len(digits) <= 15:
            cleaned_phones.append(phone.strip())

    return list(set(cleaned_phones))


def find_contact_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    keywords = ["contact", "contacts", "about", "support"]

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()

        if any(word in href for word in keywords):
            full_url = urljoin(base_url, href)
            links.append(full_url)

    return list(set(links))


def save_to_csv(data):
    with open("leads.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["source_page", "email", "phone"])

        for row in data:
            writer.writerow(row)


def add_contact(all_results, seen_contacts, source_page, email="", phone=""):
    contact_key = email if email else phone

    if contact_key and contact_key not in seen_contacts:
        all_results.append([source_page, email, phone])
        seen_contacts.add(contact_key)


def main():
    url = input("Enter company website URL: ")

    all_results = []
    seen_contacts = set()

    # 1. Main page
    html = get_html(url)

    emails = find_emails(html)
    phones = find_phones(html)

    for email in emails:
        add_contact(all_results, seen_contacts, url, email=email)

    for phone in phones:
        add_contact(all_results, seen_contacts, url, phone=phone)

    # 2. Contact/about/support pages
    contact_links = find_contact_links(html, url)

    for link in contact_links:
        html = get_html(link)

        emails = find_emails(html)
        phones = find_phones(html)

        for email in emails:
            add_contact(all_results, seen_contacts, link, email=email)

        for phone in phones:
            add_contact(all_results, seen_contacts, link, phone=phone)

    save_to_csv(all_results)

    print("Done.")
    print("Pages checked:", 1 + len(contact_links))
    print("Unique contacts found:", len(all_results))


if __name__ == "__main__":
    main()