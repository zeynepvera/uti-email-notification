
from sdks.novavision.src.helper.package import PackageHelper
from components.EmailNotification.src.models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor,  OutputImage
from components.EmailNotification.src.models.PackageModel import EmailNotification,OutputEmailNotification, EmailNotificationResponse, EmailNotificationOutputs


def build_response(context):

    outputEmailNotification=OutputEmailNotification(value=context.message)
    emailNotificationOutputs = EmailNotificationOutputs(outputEmailNotification=outputEmailNotification)
    emailNotificationResponse = EmailNotificationResponse(outputs=emailNotificationOutputs)
    emailNotification = EmailNotification(value=emailNotificationResponse)
    executor = ConfigExecutor(value=emailNotification)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel
#