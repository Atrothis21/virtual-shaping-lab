"""Protocol package exports.

Keep imports lazy to avoid package-level circular imports when protocol modules
indirectly import phase modules that depend on reward schedule factories.
"""

__all__ = ["PROTOCOL_BUILDERS", "available_protocols", "build_protocol", "validate_protocol_name"]


def __getattr__(name):
    if name in __all__:
        from protocols import catalog

        return getattr(catalog, name)
    raise AttributeError(f"module 'protocols' has no attribute '{name}'")
