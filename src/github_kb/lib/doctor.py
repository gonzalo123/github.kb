import shutil

from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound
from pydantic import BaseModel

from github_kb.settings import Settings, create_boto_session


class DiagnosticResult(BaseModel):
    name: str
    ok: bool
    message: str


def run_diagnostics(settings: Settings) -> list[DiagnosticResult]:
    results = [
        check_binary("git", settings.git_binary),
        check_binary("ripgrep", settings.rg_binary),
    ]
    results.extend(check_aws(settings))
    return results


def check_binary(name: str, command: str) -> DiagnosticResult:
    resolved = shutil.which(command)
    if resolved:
        return DiagnosticResult(name=name, ok=True, message=f"Found at {resolved}")
    return DiagnosticResult(name=name, ok=False, message=f"Command not found: {command}")


def check_aws(settings: Settings) -> list[DiagnosticResult]:
    results: list[DiagnosticResult] = []

    try:
        session = create_boto_session(settings)
    except ProfileNotFound as error:
        return [
            DiagnosticResult(
                name="aws-profile",
                ok=False,
                message=str(error),
            )
        ]

    profile_name = session.profile_name or settings.aws_profile or "default credential chain"
    results.append(
        DiagnosticResult(
            name="aws-profile",
            ok=True,
            message=f"Using {profile_name}",
        )
    )

    credentials = session.get_credentials()
    if credentials is None:
        results.append(
            DiagnosticResult(
                name="aws-credentials",
                ok=False,
                message="No AWS credentials found. Set AWS_PROFILE or configure the default AWS credential chain.",
            )
        )
        return results

    method = getattr(credentials, "method", "resolved")
    results.append(
        DiagnosticResult(
            name="aws-credentials",
            ok=True,
            message=f"Resolved via {method}",
        )
    )

    try:
        identity = session.client("sts", region_name=settings.aws_region).get_caller_identity()
        arn = identity.get("Arn", "unknown principal")
        account = identity.get("Account", "unknown account")
        results.append(
            DiagnosticResult(
                name="sts",
                ok=True,
                message=f"{arn} ({account})",
            )
        )
    except (BotoCoreError, ClientError) as error:
        results.append(
            DiagnosticResult(
                name="sts",
                ok=False,
                message=f"Unable to call STS: {error}",
            )
        )
        return results

    try:
        bedrock_client = session.client("bedrock", region_name=settings.aws_region)
        validate_bedrock_model(bedrock_client, settings.bedrock_model_id)
        results.append(
            DiagnosticResult(
                name="bedrock",
                ok=True,
                message=f"Model available: {settings.bedrock_model_id} in {settings.aws_region}",
            )
        )
    except (BotoCoreError, ClientError) as error:
        results.append(
            DiagnosticResult(
                name="bedrock",
                ok=False,
                message=f"Unable to validate model {settings.bedrock_model_id}: {error}",
            )
        )

    return results


def validate_bedrock_model(bedrock_client, model_id: str) -> None:
    if looks_like_inference_profile(model_id):
        bedrock_client.get_inference_profile(inferenceProfileIdentifier=model_id)
        return

    bedrock_client.get_foundation_model(modelIdentifier=model_id)


def looks_like_inference_profile(model_id: str) -> bool:
    prefixes = ("us.", "eu.", "apac.", "global.")
    return model_id.startswith(prefixes)
