
from pydantic import Field, validator
from typing import List, Optional, Union, Literal
from sdks.novavision.src.base.model import Package, Image, Inputs, Configs, Outputs, Response, Request, Output, Input, Config


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
    name: Literal["emailNotification"] = "emailNotification"
    value: str
    type: Literal["string"] = "string"

    class Config:
        title = "Message: "


class Subject(Config):

    """
        Subject of the email to be sent.
    """
    name: Literal["Subject"] = "Subject"
    value: str = Field(default="Notification from NovaVision")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: str = Field(default="Notification from NovaVision")

    class Config:
        title = "Subject"


class Message(Config):
    """
    Content of the message to be send.
    """
    name: Literal["Message"] = "Message"
    value: str = Field(default="This is an automated message from NovaVision.")
    type: Literal["string"] = "string"
    field: Literal["textArea"] = "textArea"
    placeHolder: str = Field(default="This is an automated message from NovaVision.")

    class Config:
        title = "Message"

class SenderEmail(Config):

    """
        The email address of the sender.
    """
    name: Literal["SenderEmail"] = "SenderEmail"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: str = Field(default="")
    class Config:
        title = "Sender Email"

class ReceiverEmail(Config):

    """
        The email address of the receiver.
    """
    name: Literal["ReceiverEmail"] = "ReceiverEmail"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: str = Field(default="")
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
    placeHolder: str = Field(default="smtp.gmail.com")
    class Config:
        title = "SMTP Server"

class SenderMailPassword(Config):

    """
        Sender e-mail password be used when authenticating to SMTP server.
    """
    name: Literal["SenderMailPassword"] = "SenderMailPassword"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: str = Field(default="")
    class Config:
        title = "Sender Mail Password"



class SMTPPort(Config):
    """SMTP server port."""
    name: Literal["SMTPPort"] = "SMTPPort"
    value: int = Field(default=465)
    type: Literal["number"] = "number"
    field: Literal["numberInput"] = "numberInput"
    placeHolder: int = Field(default=465)

    class Config:
        title = "SMTP Port"


class CcReceiverEmail(Config):
    """Optional CC recipients (comma-separated)."""
    name: Literal["CcReceiverEmail"] = "CcReceiverEmail"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: str = Field(default="cc1@example.com, cc2@example.com")

    class Config:
        title = "Cc Receiver Email"


class BccReceiverEmail(Config):
    """Optional BCC recipients (comma-separated)."""
    name: Literal["BccReceiverEmail"] = "BccReceiverEmail"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: str = Field(default="bcc1@example.com, bcc2@example.com")

    class Config:
        title = "Bcc Receiver Email"


class AdditionalPropertiesValues(Configs):
    """
    Holds optional email settings shown under the collapsible 'Additional Properties'.
    """
    smtpPort: SMTPPort
    ccReceiverEmail: Optional[CcReceiverEmail] = None
    bccReceiverEmail: Optional[BccReceiverEmail] = None


class AdditionalProperties(Config):
    """
    Collapsible group for optional fields.
    Render hint via json_schema_extra: collapsed by default.
    """
    name: Literal["AdditionalProperties"] = "AdditionalProperties"
    value: AdditionalPropertiesValues
    type: Literal["object"] = "object"
    # NOTE: 'field' rendering key depends on your UI; keep 'option' if that's what your form understands.
    field: Literal["option"] = "option"

    class Config:
        title = "Additional Properties"
        json_schema_extra = {
            "collapsed": True  # UI hint: start collapsed; safe to ignore if unsupported
        }




class EmailNotificationInputs(Inputs):
    inputImage: InputImage


class EmailNotificationConfigs(Configs):
    subject:Subject
    senderEmail:SenderEmail
    receiverEmail:ReceiverEmail
    message: Message
    smtpServer:SMTPServer
    senderMailPassword:SenderMailPassword
    additionalProperties: Optional[AdditionalProperties] = None



class EmailNotificationOutputs(Outputs):
    emailNotification: OutputEmailNotification


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
