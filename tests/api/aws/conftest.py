# import pytest
# from api.apicore import _connect as _connect_
# from api.apicore import _config as _config_


# """
# Setup the testing construct to ease future testing cases
# """


# @pytest.fixture()
# def config():
#     _config = _config_.ConfigSingleton()
#     _config.config["MOCK"] = True  # turn on mock mode
#     yield _config


# @pytest.fixture
# def test_s3_conn(config):
#     yield _connect_.get_object("AWSS3")


# @pytest.fixture
# def test_ec2_conn(config):
#     yield _connect_.get_object("AWSEC2")
