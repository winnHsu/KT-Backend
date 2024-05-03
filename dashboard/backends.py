from django.core.mail.backends.smtp import EmailBackend
import ssl


class NoTLSVerifyEmailBackend(EmailBackend):
    def open(self):
        if self.connection is not None:
            # If connection is already open, do nothing
            return False

        try:
            # Establish connection without verifying SSL certificates
            self.connection = self.connection_class(
                host=self.host,
                port=self.port,
                context=ssl._create_unverified_context(),  # Context to avoid certificate verification
            )

            # Log in to the server if username and password are provided
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
