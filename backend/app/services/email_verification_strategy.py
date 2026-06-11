class VerificationStrategy:
    def send_verification(self, user):
        raise NotImplementedError

    def verify(self, token):
        raise NotImplementedError
