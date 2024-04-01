from os import environ, getenv
from inspect import currentframe
from base64 import b64decode
from boto3 import session
from botocore.config import Config
from logging import Logger as Log
from api.apicore import _common as _common_
from api.apicore import _config as _config_

iaws_config = Config(
    region_name="us-west-2",
    signature_version="v4",
    retries={"max_attempts": 10, "mode": "standard"},
)


@_common_.exception_handlers()
def setup_session_by_profile(
    profile_name: str | None, region_name: str | None = "us-west-2"
) -> session.Session:
    """
    Initializes and returns an AWS session, optionally configured with a specified profile and region.
    This function creates an AWS session that can be used to interact with AWS services. The session can
    be optionally configured with a specific profile and region. If the profile name is provided, the session
    uses the credentials and configuration associated with that profile, typically defined in the AWS
    credentials and config files. Specifying a region name configures the session to operate within a
    specific AWS region, essential for accessing region-scoped services and resources.

    Args:
        profile_name (str | None): The name of the AWS profile to use for configuring the session.
                                   If None, the default profile or environment credentials are used.
                                   Profiles are managed through AWS configuration files.
        region_name (str | None): The name of the AWS region where the session will operate.
                                  Defaults to "us-west-2" if not specified. The region determines
                                  which geographical location the session's AWS services will interact with.
    Returns:
        session.Session: An instance of an AWS session configured with the given profile and region settings.
                         This session object can be utilized to access and manage AWS services.
    Example:
        # Initialize a session with the default profile in the 'us-west-2' region
        default_session = setup_session_by_profile(None)
        # Initialize a session with a custom profile in the 'eu-central-1' region
        custom_session = setup_session_by_profile('myCustomProfile', 'eu-central-1')

    Note:
        The AWS SDK (boto3) must be configured correctly with the necessary credentials and configurations
        for the specified profile. This involves setting up the ~/.aws/credentials and ~/.aws/config files
        with the appropriate access keys, secret keys, and other configuration details.
    """
    return session.Session(profile_name=profile_name, region_name=region_name)


@_common_.exception_handlers()
def setup_session(
    config: _config_.ConfigSingleton | None, logger: Log | None = None
) -> session.Session:
    """
    Creates an AWS session using credentials and region information from a configuration singleton or environment variables.
    This function attempts to create an AWS session by first trying to decode and use AWS credentials (access key and
    secret access key) provided by the `config` object, a ConfigSingleton instance. If the `config` does not have the
    required credentials, it falls back to environment variables. The AWS region is also set based on the `config` object
    or an environment variable, defaulting to 'us-west-2' if not specified anywhere. It ensures secure handling of credentials
    by expecting them to be base64 encoded, both in the configuration and the environment variables. On successful creation
    of the session, an informational log is generated. In case of failure, due to missing or invalid credentials, an error
    log is produced.

    Args:
        config (_config_.ConfigSingleton | None): The configuration object containing AWS credentials and region info.
                                                   If None, the function looks for credentials and region info in the
                                                   environment variables.
        logger (Log | None): An optional logger for logging the status of AWS session creation. Defaults to None, in
                             which case logging may not be performed unless a default logger is implemented in the
                             `_common_` module.
    Returns:
        session.Session: An AWS session object configured with the specified credentials and region. If the function
                         fails to create a session due to missing or invalid credentials, it may raise an exception
                         or return None, depending on the implementation of the `_common_.error_logger`.

    Note:
        - The AWS credentials (access key and secret access key) must be base64 encoded in the configuration or the
          environment variables for security reasons.
        - It's essential to have the appropriate AWS credentials and region information correctly set up either in the
          `config` object or as environment variables for the successful creation of an AWS session.

    Example:
        use environment variables:

        export AWS_ACCESS_KEY_ID=<aws access key id in base64 encoded>
        export AWS_SECRET_ACCESS_KEY=<aws access key id in base64 encoded>

    """

    access_key = b64decode(
        config.config.get("aws_access_key_id", getenv("AWS_ACCESS_KEY_ID", ""))
    ).decode("UTF-8")
    secret_access_key = b64decode(
        config.config.get("aws_secret_access_key", getenv("AWS_SECRET_ACCESS_KEY", ""))
    ).decode("UTF-8")
    region = config.config.get("aws_region_name", getenv("AWS_REGION", "us-west-2"))
    if access_key and secret_access_key:
        sess = session.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )
        _common_.info_logger(
            f"connecting to AWS region {region}, AWS session is created successfully",
            logger=logger,
        )
        return sess
    else:
        _common_.error_logger(
            currentframe().f_code.co_name,
            f"Error in working with AWS credentials.  "
            f"Please check whether the environment variable encoded AWS_ACCESS_KEY_ID and "
            f"AWS_SECRET_ACCESS_KEY is set correctly or they are in the configuration file. ",
            logger=logger,
            mode="error",
            ignore_flag=False,
        )
