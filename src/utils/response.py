
from sdks.novavision.src.helper.package import PackageHelper
from components.EmailNotification.src.models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor,  OutputImage
from components.EmailNotification.src.models.PackageModel import EmailNotification, EmailNotificationResponse, EmailNotificationOutputs


def build_response(context):
    outputImage = OutputImage(value=context.image)
    emailNotificationOutputs = EmailNotificationOutputs(outputImage=outputImage)
    emailNotificationResponse = EmailNotificationResponse(outputs=emailNotificationOutputs)
    emailNotification = EmailNotification(value=emailNotificationResponse)
    executor = ConfigExecutor(value=emailNotification)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel