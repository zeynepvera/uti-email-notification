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


def parse_recipients(value) -> list[str]:
    """'a@x.com, b@y.com; c@z.com' -> ['a@x.com', 'b@y.com', 'c@z.com']"""
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
    parts = re.split(r"[;, \s]+", str(value))
    return [p for p in parts if p]


def validate_required(cfg: dict) -> list[str]:
    return [k for k, v in cfg.items() if v in (None, "", [])]


def build_mime(from_addr: str, recipients: list[str], subject: str, body: str) -> str:
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = str(subject)
    msg.attach(MIMEText(body or "", "plain"))
    return msg.as_string()


def smtp_send(smtp_server: str, smtp_port: int, login_email: str, password: str,
              sender: str, to_addrs: list[str], raw_message: str) -> None:
    try:
        port = int(smtp_port) if smtp_port is not None else 465
    except Exception:
        port = 465

    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(login_email, password)
            server.sendmail(sender, to_addrs, raw_message)
    else:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            try:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
            except Exception:
                pass
            server.login(login_email, password)
            server.sendmail(sender, to_addrs, raw_message)


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
        self.sender_password =self.request.get_param("SenderMailPassword")

        self.message = None

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def execute(self) -> str:
        missing = validate_required({
            "Subject": self.subject,
            "Message": self.message_body,
            "SenderEmail": self.sender_email,
            "ReceiverEmail": self.receiver_email,
            "SMTPServer": self.smtp_server,
            "SenderMailPassword": self.sender_password,
        })
        if missing:
            return f"Missing required parameter(s): {', '.join(missing)}"

        recipients = parse_recipients(self.receiver_email)
        if not recipients:
            return "ReceiverEmail is empty or invalid."

        raw = build_mime(
            from_addr=self.sender_email,
            recipients=recipients,
            subject=self.subject,
            body=self.message_body,
        )

        try:
            smtp_send(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                login_email=self.sender_email,
                password=self.sender_password,
                sender=self.sender_email,
                to_addrs=recipients,
                raw_message=raw,
            )
            return f"Email sent to: {', '.join(recipients)}"
        except Exception as e:
            return f"Failed to send e-mail: {e}"

    def run(self):
        self.message = self.execute()
        return build_response(context=self)


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
