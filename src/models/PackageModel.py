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
    #field: Literal["textInput"] = "textInput"

    class Config:
        title = "Receiver Email"


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


class EmailNotificationInputs(Inputs):
    inputImage: InputImage


class EmailNotificationConfigs(Configs):
    subject: Subject
    senderEmail: SenderEmail
    receiverEmail: ReceiverEmail
    message: Message
    smtpServer: SMTPServer
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
