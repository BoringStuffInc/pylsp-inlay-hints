import itertools
from dataclasses import dataclass
from typing import Literal, TypeAlias, cast

import astroid
import astypes
from astroid.nodes import Const, FunctionDef, If, Raise, Return
from astroid.nodes.node_classes import NodeNG
from astypes._type import Type
from pylsp_inlay_hints.interfaces import InlayHint, InlayHintKind

Kind: TypeAlias = Literal["raise"] | Literal["return"] | Literal["assign"]


@dataclass
class WalkResult:
    kind: Kind
    node: NodeNG
    inferred_type: Type | None = None
    literal: str | None = None

    def to_hint(self) -> InlayHint:
        if not self.inferred_type and not self.literal:
            raise ValueError(
                "Both inferred type and literal are None for node: %s",
                self.node,
            )

        if self.literal:
            label = self.literal
        elif self.inferred_type:
            label = self.inferred_type.name

        if isinstance(self.node, FunctionDef):
            line = self.node.position.end_lineno - 1
            character = self.node.position.end_col_offset - 1
        else:
            line = self.node.end_lineno - 1
            character = self.node.end_col_offset - 1

        return {
            "position": {
                "line": line,
                "character": character,
            },
            "label": label,
            "kind": InlayHintKind.Type,
            "tooltip": None,
        }


def get_hints(source_code: str, path: str) -> list[InlayHint]:
    ast = astroid.parse(source_code, path=path)
    walk_results = _walk(ast)
    return [result.to_hint() for result in walk_results]


def _walk(
    node: NodeNG,
) -> list[WalkResult]:
    if isinstance(node, Return):
        _type = astypes.get_type(node.value)
        if isinstance(node.value, Const):
            return [
                WalkResult(
                    kind="return",
                    node=node,
                    inferred_type=_type,
                    literal=f"Literal[{node.value.value}]",
                )
            ]
        else:
            return [WalkResult(kind="return", node=node, inferred_type=_type)]
    elif isinstance(node, Raise):
        return [WalkResult(kind="raise", node=node, literal=node.exc.name)]
    elif hasattr(node, "value"):
        if isinstance(node.value, Const):
            return [
                WalkResult(
                    kind="assign", node=node, literal=f"Literal[{node.value.value}]"
                )
            ]
        else:
            _type = astypes.get_type(node.value)
            if _type is not None:
                return [WalkResult(kind="assign", node=node, inferred_type=_type)]

    hints: list[WalkResult] = []

    if isinstance(node, FunctionDef):
        annotations = []

        for body_node in node.body:
            annotations.extend(_walk(body_node))

        groups = itertools.groupby(annotations, key=lambda result: result.kind)

        for name, group in groups:
            match name:
                case "assign":
                    hints.extend(group)
                case "return":
                    return_type = _return_type(list(group), parent=node)
                    if return_type:
                        hints.append(return_type)
                case "raise":
                    hints.append(_exceptions(list(group), parent=node))
    elif isinstance(node, If):
        for body_node in node.body:
            hints.extend(_walk(body_node))
        for or_else_node in node.orelse:
            hints.extend(_walk(or_else_node))
    elif hasattr(node, "body"):
        for body_node in node.body:
            hints.extend(_walk(body_node))

    return hints


def _exceptions(results: list[WalkResult], parent: FunctionDef) -> WalkResult:
    literal = (
        "raises (" + ", ".join(cast(str, result.literal) for result in results) + ")"
    )
    return WalkResult(node=parent, kind="raise", literal=literal)


def _return_type(results: list[WalkResult], parent: FunctionDef) -> WalkResult | None:
    unique_literals = list(set(filter(None, (result.literal for result in results))))
    unique_types = list(
        set(result.inferred_type.name for result in results if result.inferred_type)
    )

    if len(unique_literals) == 1 and len(unique_types) == 1:
        return WalkResult(
            kind="return",
            node=parent,
            literal=f"-> {unique_literals[0]}",
        )
    elif len(unique_types) == 1:
        return WalkResult(
            kind="return",
            node=parent,
            literal=f"-> {unique_types[0]}",
        )
    elif len(unique_types) > 1:
        return WalkResult(
            kind="return",
            node=parent,
            literal=f"-> {'|'.join(unique_types)}",
        )
    else:
        return None
