import logging

from pylsp.workspace import Workspace
from pylsp_inlay_hints import extractor
from pylsp_inlay_hints.interfaces import InlayHint, Range, TextDocumentIdentifier
from pylsp_jsonrpc.dispatchers import MethodDispatcher

logger = logging.getLogger(__name__)


class InlayHintsDispatcher(MethodDispatcher):
    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace
        self.hints: dict[str, list[InlayHint]] = {}

    def m_text_document__inlay_hint(
        self,
        *,
        textDocument: TextDocumentIdentifier,
        range: Range,
        **kwargs,
    ) -> list[InlayHint]:
        logger.info("PyLSP Inlay Hints: dispatched textDocument/inlayHint request")
        with self.workspace.report_progress("inlay hints: astypes"):
            logger.info("PyLSP Inlay Hints: Got inlay hints request for %s", textDocument["uri"])
            document = self.workspace.get_document(textDocument["uri"])

            try:
                self.hints[document.path] = extractor.get_hints(document.source, document.path)
            except Exception as e:
                logger.error("PyLSP Inlay Hints: failed to extract type hints - %s", e)
                return []
            else:
                logger.info("PyLSP Inlay Hints: calculated inlay hints successfully")

            return [
                hint
                for hint in self.hints[document.path]
                if hint["position"]["line"] >= range["start"]["line"]
                and hint["position"]["line"] <= range["end"]["line"]
            ]
