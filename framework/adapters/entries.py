"""Generate thin provider entry text from one relative, pinned rules reference."""
import re
from .runspec import safe_relative


def render_entries(rules_path, rules_sha256):
    path = safe_relative(rules_path)
    if not isinstance(rules_sha256, str) or not re.fullmatch('[0-9a-f]{64}', rules_sha256):
        raise ValueError('rules fingerprint required')
    # No platform-specific instructions independently duplicate the business rules.
    body = ('# Shared project rules\n\n'
            'Read `' + path + '` before acting. Expected SHA256: `' + rules_sha256 + '`.\n'
            'A missing or changed rule source requires reconciliation with the protected assignment.\n'
            'This entry grants no additional execution, credential, network or spending authority.\n')
    return {'AGENTS.md': body, 'CLAUDE.md': body}
