import logging
from typing import TypedDict

from pylsp import hookimpl
from pylsp.config.config import Config
from pylsp.workspace import Workspace
from pylsp_inlay_hints.dispatcher import InlayHintsDispatcher
from pylsp_inlay_hints.interfaces import InlayHintCapabilities
from pylsp_jsonrpc.dispatchers import MethodDispatcher

logger = logging.getLogger(__name__)
logger.info("PyLSP Inlay Hints: started plugin")


class PluginCapabilities(TypedDict):
    inlayHintProvider: InlayHintCapabilities | bool


@hookimpl
def pylsp_experimental_capabilities(
    config: Config,
    workspace: Workspace,
) -> PluginCapabilities:
    logger.info("PyLSP Inlay Hints: experimental capabilities hook called")
    return {
        "inlayHintProvider": {
            "resolveProvider": False,
            "workDoneProgress": True,
        },
    }


@hookimpl
def pylsp_dispatchers(
    config: Config,
    workspace: Workspace,
) -> MethodDispatcher:
    logger.info("PyLSP Inlay Hints: dispatchers hook called")
    return InlayHintsDispatcher(workspace)
