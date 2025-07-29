import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import os

# Load secrets from environment variables
YOUR_EMAIL = os.getenv("EMAIL_USER")
APP_PASSWORD = os.getenv("EMAIL_PASS")
USERNAME = "ohmschrodinger"
CACHE_FILE = "last_problem.txt"

def get_latest_problem():
    url = f"https://leetcode.com/{USERNAME}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    problem_divs = soup.find_all("a", href=True)
    for a in problem_divs:
        href = a["href"]
        if href.startswith("/problems/"):
            return a.text.strip()

    return None

def read_last_problem():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_problem(problem_name):
    with open(CACHE_FILE, "w") as f:
        f.write(problem_name)

def send_email(problem_name):
    msg = EmailMessage()
    msg['Subject'] = f"{USERNAME} just solved a new LeetCode problem!"
    msg['From'] = YOUR_EMAIL
    msg['To'] = YOUR_EMAIL
    msg.set_content(f"""
✅ {USERNAME} just solved: {problem_name}
🔗 https://leetcode.com/problems/{'-'.join(problem_name.lower().split())}/
""")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(YOUR_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

def main():
    latest = get_latest_problem()
    if not latest:
        return

    last = read_last_problem()
    if latest != last:
        send_email(latest)
        write_last_problem(latest)

if __name__ == "__main__":
    main()
