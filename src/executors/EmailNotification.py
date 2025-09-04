

import os
import sys
import ssl
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.EmailNotification.src.utils.response import build_response
from components.EmailNotification.src.models.PackageModel import PackageModel


class EmailNotification(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))

        self.subject = self.request.get_param("Subject")
        self.message_body = self.request.get_param("Message")
        self.sender_email = self.request.get_param("SenderEmail")
        self.receiver_email = self.request.get_param("ReceiverEmail")
        self.smtp_server = self.request.get_param("SMTPServer")
        self.smtp_port = self.request.get_param("SMTPPort")
        # Modeldeki isim "SenderMailPassword"; olası eski ad için fallback:
        self.sender_password = (
            self.request.get_param("SenderMailPassword")
            or self.request.get_param("SMTPPassword")
        )

        self.message = None

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}


    @staticmethod
    def _parse_recipients(value):
        """
        "a@x.com, b@y.com; c@z.com" -> ["a@x.com","b@y.com","c@z.com"]
        """
        if value is None:
            return []
        if isinstance(value, list):
            return [v for v in value if v]
        parts = re.split(r"[;, \s]+", str(value))
        return [p for p in parts if p]

    def _smtp_send(self, sender: str, to_addrs: list[str], raw_message: str) -> None:
        """
        Port 465: SSL
        Diğer portlar: STARTTLS (örn. 587)
        """
        try:
            port = int(self.smtp_port) if self.smtp_port is not None else 465
        except Exception:
            port = 465

        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(sender, to_addrs, raw_message)
        else:
            with smtplib.SMTP(self.smtp_server, port) as server:
                server.ehlo()
                try:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.ehlo()
                except Exception:
                    pass
                server.login(self.sender_email, self.sender_password)
                server.sendmail(sender, to_addrs, raw_message)


    def run(self):
        required = {
            "Subject": self.subject,
            "Message": self.message_body,
            "SenderEmail": self.sender_email,
            "ReceiverEmail": self.receiver_email,
            "SMTPServer": self.smtp_server,
            "SenderMailPassword": self.sender_password,
        }
        missing = [k for k, v in required.items() if v in (None, "", [])]
        if missing:
            self.message = f"Missing required parameter(s): {', '.join(missing)}"
            return build_response(context=self)

        recipients = self._parse_recipients(self.receiver_email)
        if not recipients:
            self.message = "ReceiverEmail is empty or invalid."
            return build_response(context=self)

        mime = MIMEMultipart()
        mime["From"] = self.sender_email
        mime["To"] = ", ".join(recipients)
        mime["Subject"] = str(self.subject)
        mime.attach(MIMEText(self.message_body or "", "plain"))

        try:
            self._smtp_send(self.sender_email, recipients, mime.as_string())
            self.message = f"Email sent to: {', '.join(recipients)}"
        except Exception as e:
            self.message = f"Failed to send e-mail: {e}"

        return build_response(context=self)


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
