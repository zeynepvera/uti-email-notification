from pydantic import Field, validator
from typing import Optional, Union, Literal, Dict, Any
from sdks.novavision.src.base.model import Package, Inputs, Configs, Outputs, Response, Request, Output, Input, Config

class OutputEmailNotification(Output):
    name: Literal["outputEmailNotification"] = "outputEmailNotification"
    value: str
    type: Literal["string"] = "string"
    class Config:
        title = "Message: "

class Subject(Config):
    name: Literal["Subject"] = "Subject"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    class Config: title = "Subject"

class Message(Config):
    name: Literal["Message"] = "Message"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    class Config: title = "Message"

class SenderEmail(Config):
    name: Literal["SenderEmail"] = "SenderEmail"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    class Config: title = "Sender Email"

class ReceiverEmail(Config):
    name: Literal["ReceiverEmail"] = "ReceiverEmail"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    class Config: title = "Receiver Email"

class SMTPServer(Config):
    name: Literal["SMTPServer"] = "SMTPServer"
    value: str = Field(default="smtp.gmail.com")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    class Config: title = "SMTP Server"

class SenderMailPassword(Config):
    name: Literal["SenderMailPassword"] = "SenderMailPassword"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    class Config: title = "Sender Mail Password"

class SMTPPort(Config):
    name: Literal["SMTPPort"] = "SMTPPort"
    value: int = Field(default=465)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"
    class Config: title = "SMTP Port"

class EmailPayload(Input):

    name: Literal["EmailPayload"] = "EmailPayload"
    value: Union[Dict[str, Any], str, None] = None
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        v = values.get("value")
        if isinstance(v, str):
            return "string"
        return "object"

    class Config:
        title = "Email Payload"

class EmailNotificationInputs(Inputs):
    EmailPayload: Optional[EmailPayload] = None

class EmailNotificationConfigs(Configs):
    subject: Subject
    senderEmail: SenderEmail
    receiverEmail: ReceiverEmail
    message: Message
    smtpServer: SMTPServer
    smtpPort: SMTPPort
    senderMailPassword: SenderMailPassword

class EmailNotificationOutputs(Outputs):
    outputEmailNotification: OutputEmailNotification

class EmailNotificationRequest(Request):
    inputs: Optional[EmailNotificationInputs]
    configs: EmailNotificationConfigs
    class Config:
        json_schema_extra = {"target": "configs"}

class EmailNotificationResponse(Response):
    outputs: EmailNotificationOutputs

class EmailNotification(Config):
    name: Literal["EmailNotification"] = "EmailNotification"
    value: Union[EmailNotificationRequest, EmailNotificationResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"
    class Config:
        title = "EmailNotification"
        json_schema_extra = {"target": {"value": 0}}

class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[EmailNotification]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"
    class Config:
        title = "Task"
        json_schema_extra = {"target": "value"}

class PackageConfigs(Configs):
    executor: ConfigExecutor

class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["EmailNotification"] = "EmailNotification"
