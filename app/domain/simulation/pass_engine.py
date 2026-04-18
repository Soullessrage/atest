"""Base class for simulation passes and pass execution engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import List

from app.domain.simulation.context import SimulationContext


class SimulationPass(ABC):
    """
    Base class for simulation passes.
    
    Each pass represents one aspect of world simulation (e.g., NPC aging, population growth, events).
    Passes execute in order and share a mutable SimulationContext.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def apply(self, context: SimulationContext) -> None:
        """
        Apply this simulation pass to the world state.

        Args:
            context: The simulation context carrying world state and metadata.

        The pass should mutate context.world and record changes in context.changes.
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class SimulationPassEngine:
    """
    Executes a sequence of simulation passes in order.

    The same context is threaded through all passes, allowing them to coordinate
    and see the effects of previous passes.
    """

    def __init__(self, passes: List[SimulationPass] | None = None):
        self.passes = passes or []

    def add_pass(self, pass_instance: SimulationPass) -> None:
        """Register a pass to be executed."""
        self.passes.append(pass_instance)

    def execute(self, context: SimulationContext) -> SimulationContext:
        """
        Execute all passes in order, threading the context through each.

        Args:
            context: The initial simulation context.

        Returns:
            The context after all passes have executed.
        """
        for pass_instance in self.passes:
            pass_instance.apply(context)
        return context
