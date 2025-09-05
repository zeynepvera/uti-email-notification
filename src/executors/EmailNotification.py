import os
import sys
import ssl
import re
import smtplib
from typing import List, Any, Optional
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
        raw_pwd = self.request.get_param("SenderMailPassword")
        self.sender_password = self._sanitize_app_password(raw_pwd)
        self.cc_enabled_raw = self.request.get_param("CcEnabled")
        self.cc_to_raw = self.request.get_param("CcTo")
        self.bcc_enabled_raw = self.request.get_param("BccEnabled")
        self.bcc_to_raw = self.request.get_param("BccTo")

        self.message = None

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}


    @staticmethod
    def _sanitize_app_password(p: Any) -> Optional[str]:
        if p is None:
            return None
        return re.sub(r"\s+", "", str(p)).strip()

    @staticmethod
    def _parse_recipients(value: Any) -> List[str]:
        """'a@x.com, b@y.com; c@z.com' -> ['a@x.com','b@y.com','c@z.com']"""
        if value is None:
            return []
        if isinstance(value, list):
            return [v for v in value if v]
        parts = re.split(r"[;, \s]+", str(value))
        return [p for p in parts if p]

    @staticmethod
    def _validate_required(cfg: dict) -> List[str]:
        return [k for k, v in cfg.items() if v in (None, "", [])]

    @staticmethod
    def _coerce_bool(v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() == "true"
        if isinstance(v, dict):
            inner = v.get("value")
            if isinstance(inner, bool):
                return inner
            if isinstance(inner, str):
                return inner.strip().lower() == "true"
        return False

    @staticmethod
    def _build_mime(from_addr: str, to_list: List[str], cc_list: Optional[List[str]],
                    subject: str, body: str) -> str:
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = str(subject)
        msg.attach(MIMEText(body or "", "plain"))
        return msg.as_string()

    @staticmethod
    def _smtp_send(smtp_server: str, smtp_port, login_email: str, password: str,
                   sender: str, to_addrs: List[str], raw_message: str) -> None:
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

    def execute(self) -> str:
        missing = self._validate_required({
            "Subject": self.subject,
            "Message": self.message_body,
            "SenderEmail": self.sender_email,
            "ReceiverEmail": self.receiver_email,
            "SMTPServer": self.smtp_server,
            "SenderMailPassword": self.sender_password,
        })
        if missing:
            return f"Missing required parameter(s): {', '.join(missing)}"

        to_list = self._parse_recipients(self.receiver_email)
        cc_enabled = self._coerce_bool(self.cc_enabled_raw)
        cc_list = self._parse_recipients(self.cc_to_raw) if cc_enabled else []
        bcc_enabled = self._coerce_bool(self.bcc_enabled_raw)
        bcc_list = self._parse_recipients(self.bcc_to_raw) if bcc_enabled else []

        if not to_list and not cc_list and not bcc_list:
            return "No valid recipients (To/Cc/Bcc)."

        raw = self._build_mime(
            from_addr=self.sender_email,
            to_list=to_list,
            cc_list=cc_list,
            subject=self.subject,
            body=self.message_body,
        )

        envelope_addrs = to_list + cc_list + bcc_list

        try:
            self._smtp_send(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                login_email=self.sender_email,
                password=self.sender_password,
                sender=self.sender_email,
                to_addrs=envelope_addrs,
                raw_message=raw,
            )
            sent_info = []
            if to_list: sent_info.append(f"To({len(to_list)})")
            if cc_list: sent_info.append(f"Cc({len(cc_list)})")
            if bcc_list: sent_info.append(f"Bcc({len(bcc_list)})")
            return "Email sent: " + ", ".join(sent_info)
        except Exception as e:
            return f"Failed to send e-mail: {e}"

    def run(self):
        self.message = self.execute()
        return build_response(context=self)


if "__name__" == "__main__":
    Executor(sys.argv[1]).run()
