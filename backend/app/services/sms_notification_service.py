from urllib import parse, request


class SMSNotificationService:
    def __init__(self, config):
        self.account_sid = config["TWILIO_ACCOUNT_SID"]
        self.auth_token = config["TWILIO_AUTH_TOKEN"]
        self.from_number = config["TWILIO_FROM_NUMBER"]

    def send_sms(self, to_number: str, body: str) -> bool:
        if self.account_sid and self.auth_token and self.from_number:
            try:
                payload = parse.urlencode(
                    {
                        "From": self.from_number,
                        "To": to_number,
                        "Body": body,
                    }
                ).encode()

                api_request = request.Request(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json",
                    data=payload,
                    method="POST",
                )
                api_request.add_header("Content-Type", "application/x-www-form-urlencoded")

                password_manager = request.HTTPPasswordMgrWithDefaultRealm()
                password_manager.add_password(None, api_request.full_url, self.account_sid, self.auth_token)
                opener = request.build_opener(request.HTTPBasicAuthHandler(password_manager))
                with opener.open(api_request, timeout=15) as response:
                    return 200 <= response.status < 300
            except Exception as error:
                print(f"[sms error] {error}")
                return False

        print(f"[sms fallback] to={to_number} body={body}")
        return True

    def send_otp_sms(self, to_number: str, otp: str) -> bool:
        return self.send_sms(to_number, f"Your GATEMIND verification OTP is: {otp}")

    def send_reset_password_sms(self, to_number: str, otp: str) -> bool:
        return self.send_sms(to_number, f"Your GATEMIND password reset OTP is: {otp}")
