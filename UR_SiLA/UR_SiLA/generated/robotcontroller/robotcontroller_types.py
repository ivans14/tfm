# Generated by sila2.code_generator; sila2.__version__: 0.10.1
from __future__ import annotations

from typing import NamedTuple


class ConnectToRobot_Responses(NamedTuple):
    Status: str
    """
    The status of the connection
    """


class ConfigureProgram_Responses(NamedTuple):
    ConfigureProgramResponse: str
    """
    Returns the response from the program.
        
    """


class ConfigureProgram_IntermediateResponses(NamedTuple):
    CurrentStatus: str
    """
    The current status of the program
    """
