from django.core.mail.backends.smtp import EmailBackend
import ssl


class NoTLSVerifyEmailBackend(EmailBackend):
    def open(self):
        # Return immediately if a connection is already open
        if self.connection is not None:
            return False

        try:
            # Initialize SMTP connection without SSL certificate verification
            self.connection = self.connection_class(
                host=self.host,
                port=self.port,
                context=ssl._create_unverified_context(),
            )

            # Perform server login if credentials are available
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            # Reraise the exception if fail_silently is False
            if not self.fail_silently:
                raise
            return False
