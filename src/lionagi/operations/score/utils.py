# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.protocols.models import FieldModel


def validate_score(cls, value) -> list:
    return [value] if not isinstance(value, list) else value


SCORES_FIELD = FieldModel(
    name="score",
    annotation=list[float] | float,
    default_factory=list,
    description="** A numeric score or a list of numeric scores.**",
    title="Scores",
    validators=validate_score,
    validator_kwargs={"mode": "before"},
)
