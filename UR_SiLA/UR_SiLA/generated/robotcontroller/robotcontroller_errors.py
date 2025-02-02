# Generated by sila2.code_generator; sila2.__version__: 0.10.1
from __future__ import annotations

from typing import Optional

from sila2.framework.errors.defined_execution_error import DefinedExecutionError

from .robotcontroller_feature import RobotControllerFeature


class InvalidParameters(DefinedExecutionError):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "The provided parameters are not within the acceptable range"
        super().__init__(RobotControllerFeature.defined_execution_errors["InvalidParameters"], message=message)
