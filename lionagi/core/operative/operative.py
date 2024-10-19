from lionfuncs import MutableModel

from .models import (
    ACTION_REQUESTS_FIELD,
    ACTION_REQUIRED_FIELD,
    ACTION_RESPONSES_FIELD,
    REASON_FIELD,
)


class Operative(MutableModel):

    @classmethod
    def get_request_response_model(
        cls, reason: bool = False, actions: bool = False
    ):
        return cls.as_request_model(reason, actions), cls.as_response_model(
            reason, actions
        )

    @classmethod
    def as_request_model(cls, reason: bool = False, actions: bool = False):
        if reason and actions:
            return cls.new_model(
                model_name="ReAct" + cls.__name__,
                reason=REASON_FIELD,
                actions=ACTION_REQUESTS_FIELD,
                action_required=ACTION_REQUIRED_FIELD,
            )
        elif reason:
            return cls.new_model(
                model_name="Reason" + cls.__name__,
                reason=REASON_FIELD,
            )
        elif actions:
            return cls.new_model(
                model_name="Action" + cls.__name__,
                actions=ACTION_REQUESTS_FIELD,
                action_required=ACTION_REQUIRED_FIELD,
            )
        return cls.new_model(model_name=cls.__name__)

    @classmethod
    def as_response_model(cls, reason: bool = False, actions: bool = False):
        if reason and actions:
            return cls.new_model(
                model_name="ReAct" + cls.__name__,
                reason=REASON_FIELD,
                actions=ACTION_RESPONSES_FIELD,
                action_required=ACTION_REQUIRED_FIELD,
            )
        elif reason:
            return cls.new_model(
                model_name="Reason" + cls.__name__,
                reason=REASON_FIELD,
            )
        elif actions:
            return cls.new_model(
                model_name="Action" + cls.__name__,
                actions=ACTION_RESPONSES_FIELD,
                action_required=ACTION_REQUIRED_FIELD,
            )
        return cls.new_model(model_name=cls.__name__)
