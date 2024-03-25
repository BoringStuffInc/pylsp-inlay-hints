from enum import Enum
from typing import TypedDict, Union, Optional

Uri = str


class TextDocumentIdentifier(TypedDict):
    uri: Uri


class Position(TypedDict):
    line: int
    character: int


class Range(TypedDict):
    start: Position
    end: Position


class InlayHintKind(Enum):
    TYPE = 1
    PARAMETER = 2


class InlayHint(TypedDict):
    position: Position
    label: str
    kind: int
    tooltip: Optional[str]


class InlayHintCapabilities(TypedDict):
    resolveProvider: bool
    workDoneProgress: bool


class PluginCapabilities(TypedDict):
    inlayHintProvider: Union[InlayHintCapabilities, bool]
