from inspect import currentframe
from typing import List, Dict
from logging import Logger as Log
from botocore.exceptions import ClientError
from api.apicore import _meta as _meta_
from api.apicore import _common as _common_
from api.apicore import _config as _config_
from api.aws import _awsclient_config as _aws_config_


class APIObjectAWSS3(metaclass=_meta_.APIObjectMeta):
    def __init__(self, config: _config_.ConfigSingleton = None, logger: Log = None):
        self.config = config if config else _config_.ConfigSingleton()

        def get_client(client_type="s3"):
            session = (
                _aws_config_.setup_session_by_profile(
                    self.config.config.get("aws_profile_name")
                )
                if self.config.config.get("aws_profile_name")
                else _aws_config_.setup_session(self.config)
            )
            return session.client(client_type)

        self.client = _common_.mockawsclient() if self.config.config.get("MOCK") else get_client("s3")

    @_common_.exception_handlers()
    def list_bucket_names(self, logger: Log = None) -> List:
        """
        Retrieves the names of all buckets in the AWS S3 service for the configured AWS account.
        This method calls the `list_buckets` method on the class's S3 client to fetch a list of all S3 buckets
        available under the AWS account associated with the client's credentials. It parses the response to
        extract and return the bucket names. If the API call is successful but no buckets are found, an empty
        list is returned. If the API call fails or does not return a 200 OK HTTP status code, the method also
        returns an empty list but logs the error or abnormal response for debugging purposes.
        Args:
            logger (Log | None): An optional logger to log any errors encountered during the API call. If not
                                 provided, errors may be logged using a default mechanism or may not be logged
                                 at all, depending on the implementation of `_common_.error_logger`.
        Returns:
            List[str]: A list of bucket names available in the S3 service for the configured AWS account.
                       Returns an empty list if no buckets are found or if an error occurs.

        """
        try:
            _response = self.client.list_buckets()
            if _response.get("ResponseMetadata", "").get("HTTPStatusCode", -1) == 200:
                return [
                    _each_bucket.get("Name")
                    for _each_bucket in _response.get("Buckets", [])
                ]
            else:
                return []

        except ClientError as err:
            _common_.error_logger(
                currentframe().f_code.co_name,
                err,
                logger=logger,
                mode="error",
                ignore_flag=False,
            )
