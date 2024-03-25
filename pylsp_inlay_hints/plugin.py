from pylsp import hookimpl
from pylsp.config.config import Config
from pylsp.workspace import Workspace
from pylsp_inlay_hints.dispatcher import InlayHintsDispatcher
from pylsp_inlay_hints.interfaces import PluginCapabilities
from pylsp_jsonrpc.dispatchers import MethodDispatcher


_capabilities: PluginCapabilities = {
    "inlayHintProvider": {
        "resolveProvider": False,
        "workDoneProgress": True,
    },
}


@hookimpl
def pylsp_experimental_capabilities(config: Config, workspace: Workspace) -> PluginCapabilities:
    return _capabilities


@hookimpl
def pylsp_dispatchers(config: Config, workspace: Workspace) -> MethodDispatcher:
    return InlayHintsDispatcher(workspace)
