from pydantic import Field, validator
from typing import List, Optional, Union, Literal
from sdks.novavision.src.base.model import Package, Image, Inputs, Configs, Outputs, Response, Request, Output, Input, \
    Config


class InputImage(Input):
    name: Literal["inputImage"] = "inputImage"
    value: Union[List[Image], Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"

    class Config:
        title = "Image"


class OutputEmailNotification(Output):
    name: Literal["outputEmailNotification"] = "outputEmailNotification"
    value: str
    type: Literal["string"] = "string"

    class Config:
        title = "Message: "


class Subject(Config):
    """
    Subject of the email to be sent.
    """
    name: Literal["Subject"] = "Subject"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Subject"


class Message(Config):
    """
    Content of the message to be send.
    """
    name: Literal["Message"] = "Message"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Message"

class MessageHtml(Config):
    """Optional HTML body."""
    name: Literal["MessageHtml"] = "MessageHtml"
    value: Optional[str] = None
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Message (HTML) - Optional"

class SenderEmail(Config):
    """
        The email address of the sender.
    """
    name: Literal["SenderEmail"] = "SenderEmail"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Sender Email"


class ReceiverEmail(Config):
    """
        The email address of the receiver.
    """
    name: Literal["ReceiverEmail"] = "ReceiverEmail"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Receiver Email"


class CCReceiverEmail(Config):
    """Optional CC addresses."""
    name: Literal["CCReceiverEmail"] = "CCReceiverEmail"
    value: Optional[str] = None
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "CC (optional)"


class BCCReceiverEmail(Config):

    """Optional BCC addresses."""
    name: Literal["BCCReceiverEmail"] = "BCCReceiverEmail"
    value: Optional[str] = None
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "BCC (optional)"


class SMTPServer(Config):
    """
        Custom SMTP server to be used.

    """
    name: Literal["SMTPServer"] = "SMTPServer"
    value: str = Field(default="smtp.gmail.com")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "SMTP Server"


class SenderMailPassword(Config):
    """
        Sender e-mail password be used when authenticating to SMTP server.
    """
    name: Literal["SenderMailPassword"] = "SenderMailPassword"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Sender Mail Password"


class SMTPPort(Config):
    """SMTP server port."""
    name: Literal["SMTPPort"] = "SMTPPort"
    value: int = Field(default=465)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "SMTP Port"


class EmailNotificationInputs(Inputs):
    inputImage: InputImage


class EmailNotificationConfigs(Configs):
    subject: Subject
    senderEmail: SenderEmail
    receiverEmail: ReceiverEmail
    ccReceiverEmail: Optional[CCReceiverEmail] = None
    bccReceiverEmail: Optional[BCCReceiverEmail] = None
    message: Message
    messageHtml: Optional[MessageHtml] = None
    smtpServer: SMTPServer
    smtpPort: SMTPPort
    senderMailPassword: SenderMailPassword


class EmailNotificationOutputs(Outputs):
    outputEmailNotification: OutputEmailNotification


class EmailNotificationRequest(Request):
    inputs: Optional[EmailNotificationInputs]
    configs: EmailNotificationConfigs

    class Config:
        json_schema_extra = {
            "target": "configs"
        }


class EmailNotificationResponse(Response):
    outputs: EmailNotificationOutputs


class EmailNotification(Config):
    name: Literal["EmailNotification"] = "EmailNotification"
    value: Union[EmailNotificationRequest, EmailNotificationResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "EmailNotification"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }


class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[EmailNotification]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Task"
        json_schema_extra = {
            "target": "value"
        }


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["EmailNotification"] = "EmailNotification"
