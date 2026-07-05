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
    "cache",
    "logs",
    "node_modules",
    "sessions",
    "tmp",
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
