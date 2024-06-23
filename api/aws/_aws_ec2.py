from inspect import currentframe
from typing import List, Dict, Union
from logging import Logger as Log
from botocore.exceptions import ClientError
from api.apicore import _meta as _meta_
from api.apicore import _common as _common_
from api.apicore import _config as _config_
from api.aws import _awsclient_config as _aws_config_


class APIObjectAWSS3(metaclass=_meta_.APIObjectMeta):
    def __init__(self, config: _config_.ConfigSingleton = None, logger: Log = None):
        self.config = config if config else _config_.ConfigSingleton()
        # self.session = _aws_config_.setup_session_by_profile(self.config.config.get("aws_profile_name")) if \
        #     self.config.config.get("aws_profile_name") else _aws_config_.setup_session(self.config)
        # self.client = self.session.client("ec2")
        def get_client(client_type="ec2"):
            session = (
                _aws_config_.setup_session_by_profile(
                    self.config.config.get("aws_profile_name")
                )
                if self.config.config.get("aws_profile_name")
                else _aws_config_.setup_session(self.config)
            )
            return session.client(client_type)

        self.client = _common_.mockawsclient() if self.config.config.get("MOCK") else get_client("ec2")

    def describe_instance(self,
                          instance_ids: Union[str, List],
                          tag_column: str = None,
                          logger: Log = None
                          ) -> Dict:
        """ This method retrieves detailed information about one or more EC2 instances specified by their instance IDs.
            It handles both single string ID and a list of IDs. If a string ID is provided, it converts it to a list.
            The method calls the AWS describe_instances API and returns the response in the form of a dictionary.
            If an error occurs during the API call, it logs the error using a provided logger.

        Args:
                instance_ids (Union[str, List]): A single instance ID as a string or multiple instance IDs as a list.
                tag_column (str, optional): An optional tag column parameter. (Currently not used in the method)
                logger (Log, optional): An optional logger for logging errors.

        Returns:
                Dict: A dictionary containing the response from the describe_instances API call.
        Raises:
                ClientError: logs the error details using the error_logger method.

        """
        try:
            if isinstance(instance_ids, str):
                instance_ids = [instance_ids]

            _parameters = {"InstanceIds": instance_ids}
            return self.client.describe_instances(**_parameters)

        except ClientError as err:
            _common_.error_logger(currentframe().f_code.co_name,
                                  err,
                                  logger=logger,
                                  mode="error",
                                  ignore_flag=False)
