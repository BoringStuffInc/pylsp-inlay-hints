from enum import IntEnum
from typing import TypeAlias, TypedDict

Uri: TypeAlias = str


class TextDocumentIdentifier(TypedDict):
    uri: Uri


class Position(TypedDict):
    line: int
    character: int


class Range(TypedDict):
    start: Position
    end: Position


class InlayHintKind(IntEnum):
    Type = 1
    Parameter = 2


class InlayHint(TypedDict):
    position: Position
    label: str
    kind: InlayHintKind
    tooltip: str | None


class InlayHintCapabilities(TypedDict):
    resolveProvider: bool
    workDoneProgress: bool
