class SafeNameMixin:
    """Shared helper methods for sanitizing WebDAV-visible names."""

    @staticmethod
    def sanitize_name(name, fallback):
        """Replaces backslashes and normalizes empty names, preserves '/' for folder semantics."""
        if not name:
            name = fallback
        sanitized = str(name).replace("\\", "_").strip()
        return sanitized or fallback

    @classmethod
    def unique_safe_name(cls, original_name, fallback, existing_names, unique_suffix=None):
        """
        Returns a sanitized, unique name for WebDAV display.

        If the sanitized name already exists, it appends a stable suffix or
        an incrementing counter to ensure each exposed WebDAV name remains unique.
        """
        base_name = cls.sanitize_name(original_name, fallback)

        if base_name not in existing_names:
            existing_names.add(base_name)
            return base_name

        suffix = unique_suffix if unique_suffix is not None else "duplicate"
        candidate = f"{base_name} [{suffix}]"
        counter = 2

        while candidate in existing_names:
            candidate = f"{base_name} [{suffix}-{counter}]"
            counter += 1

        existing_names.add(candidate)
        return candidate