import os, sys, ssl, re, json, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.EmailNotification.src.utils.response import build_response
from components.EmailNotification.src.models.PackageModel import PackageModel
from sdks.novavision.src.base.application import Application

PARAM_RE = re.compile(r"{{\s*\$parameters\.([A-Za-z_]\w*)\s*}}")

def render_message(template: str, parameters: dict | None) -> str:
    if not parameters:
        return template
    def _replace(m: re.Match) -> str:
        k = m.group(1)
        return str(parameters[k]) if k in parameters else m.group(0)
    return PARAM_RE.sub(_replace, template)

class EmailNotification(Component):
    application = Application()

    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))

        # Configs
        self.subject = self.request.get_param("Subject")
        self.message_body = self.request.get_param("Message")
        self.sender_email = self.request.get_param("SenderEmail")
        self.receiver_email = self.request.get_param("ReceiverEmail")
        self.smtp_server = self.request.get_param("SMTPServer")
        self.smtp_port = self.request.get_param("SMTPPort")
        self.sender_password = self.request.get_param("SenderMailPassword")

        # Tek giriş
        self.payload = self.request.get_param("EmailPayload")  # dict | str | None

        self.message = None  # response için

    @staticmethod
    def bootstrap(config: dict):
        return {}

    @staticmethod
    def _parse_recipients(value):
        if value is None:
            return []
        if isinstance(value, list):
            return [v for v in value if v]
        import re as _re
        parts = _re.split(r"[;, \n\r\t]+", str(value))
        return [p for p in parts if p]

    def _smtp_send(self, sender: str, to_addrs: list[str], raw_message: str) -> None:
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
        # 1) payload'ı ayrıştır
        params_dict, attachments_dict, disable_flag = None, None, False

        if isinstance(self.payload, str):
            # Basit string: {{ $parameters.payload }} ile erişilebilir
            params_dict = {"payload": self.payload}

        elif isinstance(self.payload, dict):
            if any(k in self.payload for k in ("parameters", "attachments", "disable")):
                params_dict = self.payload.get("parameters")
                attachments_dict = self.payload.get("attachments")
                disable_flag = bool(self.payload.get("disable", False))
            else:
                # Düz dict'i doğrudan parameters say
                params_dict = self.payload

        # 2) disable?
        if disable_flag:
            self.message = "Sink disabled by input."
            return build_response(context=self)

        # 3) zorunlu config kontrolü
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

        # 4) templating
        body = render_message(str(self.message_body), params_dict)

        # 5) MIME oluştur
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = str(self.subject)
        msg.attach(MIMEText(body, "plain"))

        # 6) ekler
        if isinstance(attachments_dict, dict):
            for name, content in attachments_dict.items():
                part = MIMEBase("application", "octet-stream")
                payload = content if isinstance(content, (bytes, bytearray)) else str(content).encode("utf-8")
                part.set_payload(payload)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{name}"')
                msg.attach(part)

        # 7) gönder
        try:
            self._smtp_send(self.sender_email, recipients, msg.as_string())
            self.message = f"Email sent to: {', '.join(recipients)}"
        except Exception as e:
            self.message = f"Failed to send e-mail: {e}"

        return build_response(context=self)


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
