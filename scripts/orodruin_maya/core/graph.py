from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union
from uuid import UUID

import attr
from orodruin.core import Graph
from orodruin.core.graph import GraphLike

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


@attr.s
class OMGraph:
    """Orodruin Maya Graph handling the events from the Orodruin Graph."""

    _om_state: OMState = attr.ib()
    _uuid: UUID = attr.ib()

    @classmethod
    def from_graph(cls, om_state: OMState, graph: Graph) -> OMGraph:
        return cls(om_state, graph.uuid())

    def uuid(self) -> UUID:
        return self._uuid


OMGraphLike = Union[OMGraph, GraphLike]

__all__ = ["OMGraph", "OMGraphLike"]
