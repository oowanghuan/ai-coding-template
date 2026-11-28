# WP-301 provider interfaces

This implementation provides pure classification, bounded run proposals, output validation and same-source entry generation. It starts no provider, uses no API and changes no task authority. Public Python imports are available from `framework.adapters`; `AdapterRegistry` is the N-provider boundary, while Claude/Codex are two concrete implementations. A third explicit synthetic adapter shares the same registry interface. Integration belongs to the separately reviewed lifecycle/launcher.

```python
result = classify_result(
    "codex", captured_bytes,
    exit_code=observed_exit, observed_at="2026-11-27T00:00:00Z",
    protocol="codex-exec", evidence_level="untrusted_stdout",
)
```

A trusted launcher may set `provider_protocol` only after establishing actual event-channel provenance. Test callers use `synthetic_fixture`. `supervisor_reason` accepts only a caller-observed network error, local budget exhaustion or interruption; it is not read from provider output. A classification is never a command to release a lease or auto-retry.

See [shared boundary](PROTOCOL.md) and [official support inventory](OFFICIAL_SUPPORT.md). `tests/adapters/` uses clearly synthetic JSON events and makes no model calls. Authentic provider execution, complete configuration isolation, live quota handling and actual cross-model review remain unverified.
