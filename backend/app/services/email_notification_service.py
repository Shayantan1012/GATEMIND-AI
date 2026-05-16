import os
import smtplib
from email.mime.text import MIMEText

from app.config import Config


class EmailNotificationService:
    def __init__(self):
        self.smtp_host = Config.EMAIL_SMTP_HOST
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.smtp_username = Config.EMAIL_SMTP_USERNAME
        self.smtp_password = Config.EMAIL_SMTP_PASSWORD
        self.from_address = Config.EMAIL_FROM_ADDRESS

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        if self.smtp_host and self.smtp_username and self.smtp_password:
            try:
                message = MIMEText(body)
                message["Subject"] = subject
                message["From"] = self.from_address
                message["To"] = to_email

                with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(self.smtp_username, self.smtp_password)
                    smtp.sendmail(self.from_address, [to_email], message.as_string())
                return True
            except Exception as error:
                print(f"[email error] {error}")
                return False

        print(f"[email] to={to_email} subject={subject} body={body}")
        return True

    def send_otp_email(self, to_email: str, otp: str) -> bool:
        return self.send_email(to_email, "Your GATEMIND verification OTP", f"Your OTP is: {otp}")

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        return self.send_email(to_email, "Verify your GATEMIND email", verification_link)

    def send_reset_password_email(self, to_email: str, reset_link: str) -> bool:
        return self.send_email(to_email, "Reset your GATEMIND password", reset_link)
