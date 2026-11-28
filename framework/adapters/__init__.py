"""Pure planning/parsing adapters. No provider process or authority mutation."""
from .results import classify_result
from .runspec import build_run_spec, parse_proposal
from .entries import render_entries
from .registry import AdapterRegistry, default_registry, descriptor, CAPABILITIES

__all__ = ['classify_result', 'build_run_spec', 'parse_proposal', 'render_entries', 'AdapterRegistry', 'default_registry', 'descriptor', 'CAPABILITIES']
