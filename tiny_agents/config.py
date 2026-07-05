from pathlib import Path

DEFAULT_ROOTS = [
    Path.home() / ".codex",
    Path.home() / ".agents",
]

EXCLUDED_PARTS = {
    ".git",
    ".system",
    ".tmp",
    "__pycache__",
    "backups",
    "cache",
    "logs",
    "node_modules",
    "plugins",
    "sessions",
    "tmp",
    "vendor_imports",
}

SENSITIVE_PARTS = {
    ".env",
    "auth",
    "credential",
    "credentials",
    "key",
    "keys",
    "secret",
    "secrets",
    "token",
    "tokens",
}
