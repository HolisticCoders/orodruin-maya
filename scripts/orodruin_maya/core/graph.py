from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union
from uuid import UUID

from orodruin.core import Graph
from orodruin.core.graph import GraphLike

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


@dataclass
class OMGraph:
    """Orodruin Maya Graph handling the events from the Orodruin Graph."""

    _om_state: OMState
    _uuid: UUID

    @classmethod
    def from_graph(cls, om_state: OMState, graph: Graph) -> OMGraph:
        return cls(om_state, graph.uuid())

    def uuid(self) -> UUID:
        return self._uuid


OMGraphLike = Union[OMGraph, GraphLike]

__all__ = ["OMGraph", "OMGraphLike"]
