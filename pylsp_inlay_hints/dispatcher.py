import logging

from pylsp.workspace import Workspace
from pylsp_inlay_hints import extractor
from pylsp_inlay_hints.interfaces import InlayHint, Range, TextDocumentIdentifier
from pylsp_jsonrpc.dispatchers import MethodDispatcher
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class InlayHintsDispatcher(MethodDispatcher):
    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace
        self.hints: Dict[str, List[InlayHint]] = {}

    def m_text_document__inlay_hint(
        self,
        *,
        textDocument: TextDocumentIdentifier,
        range: Range,
        **kwargs: Dict[str, Any],
    ) -> List[InlayHint]:
        with self.workspace.report_progress("inlay hints: astypes"):
            document = self.workspace.get_document(textDocument["uri"])

            try:
                self.hints[document.path] = extractor.get_hints(document.source, document.path)
            except Exception as e:
                logger.error("[PyLSP Inlay Hints] Error while extracting inlay hints: %s", e)
                return []

            return [
                hint
                for hint in self.hints[document.path]
                if hint["position"]["line"] >= range["start"]["line"]
                and hint["position"]["line"] <= range["end"]["line"]
            ]
