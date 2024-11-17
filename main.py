from dotenv import load_dotenv
load_dotenv()

import imaplib
import email
import os
from bs4 import BeautifulSoup
import requests

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def connect_to_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail

def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = [link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
    return links

def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print(f"Successfully visited: {link}")
        else:
            print(f"Failed to visit: {link}\nError: {response.status_code}")
    except Exception as e:
        print(f"Error With: {link}, {str(e)}")
        
        return response.status_code


def search_for_emails(limit=10):
    mail = connect_to_email()
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()

    # Limit number of emails to process
    data = data[:limit]  # Only process first 'limit' emails
    print(f"Processing {len(data)} out of {len(search_data[0].split())} emails")

    links = []

    for num in data:
        try:
            print(f'Processing email {len(links) + 1} of {limit}')
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        try:
                            # Try different encodings
                            try:
                                html_content = part.get_payload(decode=True).decode('utf-8')
                            except UnicodeDecodeError:
                                html_content = part.get_payload(decode=True).decode('latin-1')
                            links.extend(extract_links_from_html(html_content))
                        except Exception as e:
                            print(f"Error processing part: {e}")
                            continue
            else:
                if msg.get_content_type() == "text/html":
                    try:
                        try:
                            content = msg.get_payload(decode=True).decode('utf-8')
                        except UnicodeDecodeError:
                            content = msg.get_payload(decode=True).decode('latin-1')
                        links.extend(extract_links_from_html(content))
                    except Exception as e:
                        print(f"Error processing content: {e}")
                        continue
        except Exception as e:
            print(f"Error processing email number {num}: {e}")
            continue

    mail.logout()
    return links

def save_links(links):
    with open("links.txt", "w") as file:
        file.write("\n".join(links))


links = search_for_emails()
for link in links:
    click_link(link)

save_links(links)

# print(links)