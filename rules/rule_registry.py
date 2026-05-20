"""Registry mapping state codes to their StateRule strategy implementations."""
from __future__ import annotations

from rules.base_rule import StateRule
from rules.state_rules._stub import StubStateRule
from rules.state_rules.california import CaliforniaRule
from rules.state_rules.florida import FloridaRule
from rules.state_rules.new_york import NewYorkRule
from rules.state_rules.texas import TexasRule


class RuleRegistry:
    """Maps state codes to concrete StateRule strategies.

    Adding a new state: create a rule module in state_rules/, then call
    registry.register("XX", NewStateRule()) — nothing else changes.
    """

    def __init__(self) -> None:
        self._rules: dict[str, StateRule] = {}

    def register(self, state_code: str, rule: StateRule) -> None:
        self._rules[state_code.upper()] = rule

    def get(self, state_code: str) -> StateRule:
        """Return the rule for the given state. Falls back to StubStateRule if not registered."""
        return self._rules.get(state_code.upper(), StubStateRule(state_code))

    def registered_states(self) -> list[str]:
        return list(self._rules.keys())


def build_default_registry() -> RuleRegistry:
    """Build and return the registry pre-loaded with all known state rules."""
    registry = RuleRegistry()
    registry.register("CA", CaliforniaRule())
    registry.register("TX", TexasRule())
    registry.register("NY", NewYorkRule())
    registry.register("FL", FloridaRule())
    return registry


# Module-level singleton for convenience
default_registry = build_default_registry()
