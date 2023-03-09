import requests, smtplib

from typing import List
from email.message import EmailMessage

from settings import EMAIL_ADDRESS, EMAIL_PASSWORD, IPO_NOTIFIER_BACKEND

def get_user_email_list() -> List:
    url = IPO_NOTIFIER_BACKEND + '/api/users/'
    users = requests.get(url=url).json()
    user_emails = [user['email'] for user in users]
    return user_emails

class EmailService:

    def __init__(self, message: str) -> None:
        self.ipo_str = message

    def generate_email_message(self, receiver: str) -> str:
        message = f"This Email is to Notify you to apply in the new IPO.\n\nIPO Details:\n{self.ipo_str}\n\nYours Always,\nLaxman Maharjan"
        msg = EmailMessage()
        msg['Subject'] = "New IPO Information"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver
        msg.set_content(message)
        return msg

    def send_mail(self, receiver: str):
        message = self.generate_email_message(receiver=receiver)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(message)
    
    def send_mail_to_users(self):
        user_emails = get_user_email_list()

        for user_email in user_emails:
            self.send_mail(receiver=user_email)