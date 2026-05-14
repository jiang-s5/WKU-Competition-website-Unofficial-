import json

from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
from alibabacloud_tea_openapi import models as open_api_models


class SmsConfigurationError(RuntimeError):
    pass


class SmsSendError(RuntimeError):
    pass


def sms_is_configured(config, purpose):
    provider = config.get("SMS_PROVIDER", "demo")
    if provider != "aliyun":
        return False
    if not config.get("SMS_ACCESS_KEY_ID") or not config.get("SMS_ACCESS_KEY_SECRET"):
        return False
    if not config.get("SMS_SIGN_NAME"):
        return False
    if purpose == "register":
        return bool(config.get("SMS_TEMPLATE_CODE_REGISTER"))
    if purpose == "reset":
        return bool(config.get("SMS_TEMPLATE_CODE_RESET"))
    return False


def _template_code_for_purpose(config, purpose):
    if purpose == "register":
        return config.get("SMS_TEMPLATE_CODE_REGISTER", "")
    if purpose == "reset":
        return config.get("SMS_TEMPLATE_CODE_RESET", "")
    raise SmsConfigurationError(f"Unsupported SMS purpose: {purpose}")


def _build_client(config):
    if not config.get("SMS_ACCESS_KEY_ID") or not config.get("SMS_ACCESS_KEY_SECRET"):
        raise SmsConfigurationError("Missing SMS access key configuration.")
    endpoint = config.get("SMS_ENDPOINT", "dysmsapi.aliyuncs.com")
    sdk_config = open_api_models.Config(
        access_key_id=config["SMS_ACCESS_KEY_ID"],
        access_key_secret=config["SMS_ACCESS_KEY_SECRET"],
        endpoint=endpoint,
    )
    return DysmsapiClient(sdk_config)


def send_sms_code(config, phone, purpose, code):
    if not sms_is_configured(config, purpose):
        raise SmsConfigurationError("Aliyun SMS configuration is incomplete.")

    client = _build_client(config)
    request = dysmsapi_models.SendSmsRequest(
        phone_numbers=phone,
        sign_name=config["SMS_SIGN_NAME"],
        template_code=_template_code_for_purpose(config, purpose),
        template_param=json.dumps(
            {config.get("SMS_TEMPLATE_PARAM_KEY", "code"): code},
            ensure_ascii=False,
        ),
    )
    response = client.send_sms(request)
    body = getattr(response, "body", None)
    status_code = getattr(body, "code", "")
    if status_code != "OK":
        message = getattr(body, "message", "Unknown SMS error")
        request_id = getattr(body, "request_id", "")
        raise SmsSendError(f"{message} ({request_id})".strip())
    return body
