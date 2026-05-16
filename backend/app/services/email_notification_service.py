class EmailNotificationService:
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        print(f"[email] to={to_email} subject={subject} body={body}")
        return True

    def send_otp_email(self, to_email: str, otp: str) -> bool:
        return self.send_email(to_email, "Verify your GATEMIND account", f"Your OTP is {otp}")

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        return self.send_email(to_email, "Verify your email", verification_link)

    def send_reset_password_email(self, to_email: str, reset_link: str) -> bool:
        return self.send_email(to_email, "Reset your password", reset_link)
