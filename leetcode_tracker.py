import requests
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import time

class LeetCodeTracker:
    def __init__(self, username, email_to, smtp_email, smtp_password):
        self.username = username
        self.email_to = email_to
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.storage_file = 'last_submissions.json'
        
    def get_recent_submissions(self):
        """Fetch recent AC submissions from LeetCode profile"""
        try:
            # LeetCode GraphQL endpoint
            url = "https://leetcode.com/graphql"
            
            query = """
            query recentAcSubmissions($username: String!, $limit: Int!) {
                recentAcSubmissionList(username: $username, limit: $limit) {
                    id
                    title
                    titleSlug
                    timestamp
                }
            }
            """
            
            variables = {
                "username": self.username,
                "limit": 20  # Get last 20 submissions to be safe
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']['recentAcSubmissionList']:
                    return data['data']['recentAcSubmissionList']
                else:
                    print("No recent submissions found or API returned empty data")
                    return []
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching submissions: {str(e)}")
            return []
    
    def load_last_submissions(self):
        """Load previously seen submissions from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading last submissions: {str(e)}")
            return []
    
    def save_last_submissions(self, submissions):
        """Save current submissions to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(submissions, f, indent=2)
        except Exception as e:
            print(f"Error saving submissions: {str(e)}")
    
    def send_email(self, new_submissions):
        """Send email notification for new submissions"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_email
            msg['To'] = self.email_to
            msg['Subject'] = f"🎉 New LeetCode Solutions by {self.username}!"
            
            # Create email body
            body = f"Hello!\n\n{self.username} has solved new LeetCode problems:\n\n"
            
            # IST timezone (UTC+5:30)
            ist = timezone(timedelta(hours=5, minutes=30))
            
            for submission in new_submissions:
                timestamp = datetime.fromtimestamp(int(submission['timestamp']), tz=ist)
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S IST")
                body += f"✅ Problem: {submission['title']}\n"
                body += f"   Solved at: {formatted_time}\n"
                body += f"   Link: https://leetcode.com/problems/{submission['titleSlug']}/\n\n"
            
            body += f"Keep up the great work!\n\nHappy Coding! 🚀"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.smtp_email, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_email, self.email_to, text)
            server.quit()
            
            print(f"Email sent successfully for {len(new_submissions)} new submissions!")
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
    
    def check_for_new_submissions(self):
        """Main function to check for new submissions and send notifications"""
        print(f"Checking for new submissions for user: {self.username}")
        
        # Get current submissions
        current_submissions = self.get_recent_submissions()
        
        if not current_submissions:
            print("No submissions found or error occurred")
            return
        
        # Load last seen submissions
        last_submissions = self.load_last_submissions()
        
        # If this is the first run (no previous data), just save current state without sending email
        if not last_submissions:
            print("First run detected - saving current submissions without sending email")
            self.save_last_submissions(current_submissions)
            return
        
        # Find new submissions
        last_submission_ids = {sub['id'] for sub in last_submissions}
        new_submissions = [sub for sub in current_submissions if sub['id'] not in last_submission_ids]
        
        if new_submissions:
            print(f"Found {len(new_submissions)} new submissions!")
            
            # Sort by timestamp (newest first)
            new_submissions.sort(key=lambda x: int(x['timestamp']), reverse=True)
            
            # Send email notification
            self.send_email(new_submissions)
            
            # Save current submissions
            self.save_last_submissions(current_submissions)
        else:
            print("No new submissions found.")

def main():
    # Get environment variables
    username = os.getenv('LEET_USER')
    email_to = os.getenv('EMAIL_USER')
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_email or not smtp_password:
        print("Error: SMTP_EMAIL and SMTP_PASSWORD environment variables must be set")
        return
    
    # Create tracker instance
    tracker = LeetCodeTracker(username, email_to, smtp_email, smtp_password)
    
    # Check for new submissions
    tracker.check_for_new_submissions()

if __name__ == "__main__":
    main()
