# 📬 Email Summary Automation Tool

This project is a Python-based automation script that fetches unread emails from your Gmail inbox, summarizes them (sender, subject, and preview), and sends the summary to a specified recipient daily.

## 🚀 Features

- 🔐 Securely connects to your Gmail inbox via IMAP
- 📥 Fetches and parses the latest unread emails
- 🧠 Summarizes each email (From, Subject, Snippet)
- 📤 Sends a beautiful HTML email with the summary
- 🕒 Automatically runs daily at your set time using `schedule`

---

## 🛠️ Built With

- `imaplib` – For accessing Gmail inbox
- `email` – To parse and decode emails
- `smtplib` – To send emails
- `email.mime` – For constructing HTML messages
- `schedule` – To schedule tasks
- `getpass` – For secure password input
- `logging` – For tracking and debugging

---

## ⚠️ Notes

- Make sure **IMAP access** is enabled in your Gmail settings.
- You might need to enable **"Less secure app access"** or use **App Passwords** if you have 2FA enabled.
- Never hardcode your passwords. Use environment variables or secret managers in production.


## 📄 License

This project is licensed under the MIT License.
