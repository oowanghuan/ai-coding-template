"""Planning/parsing plus explicitly bound invocation; default adapters do not execute."""
from .results import classify_result
from .runspec import build_run_spec, parse_proposal
from .entries import render_entries
from .registry import AdapterRegistry, default_registry, descriptor, CAPABILITIES

__all__ = ['classify_result', 'build_run_spec', 'parse_proposal', 'render_entries', 'AdapterRegistry', 'default_registry', 'descriptor', 'CAPABILITIES']
