import imaplib
import email
from email.header import decode_header
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import getpass

# Setup logging
logging.basicConfig(level=logging.INFO)

# Global variables (they'll be set by user input)
sender_email = ""
sender_password = ""
receiver_email = ""

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

def fetch_unread_emails(sender_email, sender_password):
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(sender_email, sender_password)
        status, messages = imap.select("INBOX")

        emails_info = []

        # Total number of emails
        messages = int(messages[0])

        # Fetch unread emails
        status, response = imap.search(None, '(UNSEEN)')
        unread_msg_nums = response[0].split()

        logging.info(f"Found {len(unread_msg_nums)} unread emails")

        for num in unread_msg_nums[-10:]:  # Only last 10 unread
            res, msg = imap.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")

                    # Try to get a small snippet (first few lines of the email)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            try:
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    small_info = body[:200] if body else "No preview available."

                    emails_info.append({
                        "subject": subject,
                        "from": from_,
                        "snippet": small_info.strip()
                    })
        
        imap.logout()
        return emails_info

    except Exception as e:
        logging.error(f"Error fetching emails: {e}")
        return []

def send_email(subject, body, sender_email, sender_password, receiver_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        logging.info(f"Summary sent successfully to {receiver_email}")

    except Exception as e:
        logging.error(f"Error sending email: {e}")

def job():
    emails_info = fetch_unread_emails(sender_email, sender_password)

    if not emails_info:
        logging.warning("No unread emails found.")
        return

    # Prepare HTML email content
    email_content = ""

    for mail in emails_info:
        email_content += f"""
        <p>
            <strong style="font-size:16px;">Subject:</strong> <span style="font-size:16px;">{mail['subject']}</span><br>
            <strong style="color:blue;">From:</strong> <a href="mailto:{mail['from']}">{mail['from']}</a><br>
            <strong>Small Info:</strong> {mail['snippet']}<br>
        </p>
        <hr style="border:1px solid #ccc;">
        """

    # Final HTML body
    html_body = f"""
    <html>
    <body>
    {email_content}
    </body>
    </html>
    """

    # Send the summary email
    send_email("Unread Emails Summary", html_body, sender_email, sender_password, receiver_email)

def main():
    global sender_email, sender_password, receiver_email

    print("=== Email Summary Sender Setup ===")
    sender_email = input("Enter your email address (sender): ")
    sender_password = getpass.getpass("Enter your app password (not your email password!): ")
    receiver_email = input("Enter receiver's email address: ")

    # Schedule job every day at a specific time
    schedule_time = input("Enter the time to send summary daily (HH:MM format, 24-hr): ")
    try:
        schedule.every().day.at(schedule_time).do(job)
    except Exception as e:
        logging.error(f"Invalid time format. Example format: 18:32")
        return

    logging.info(f"Scheduler started. Summary will be sent every day at {schedule_time}.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()