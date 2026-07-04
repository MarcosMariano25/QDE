"""Paintable AI entry point.

Bootstraps the application and exits with its return code.
"""

from app.core.application import Application


def main() -> int:
    """Create and run the application.

    Returns:
        Process exit code from the Qt event loop.
    """
    application = Application()
    return application.run()


if __name__ == "__main__":
    raise SystemExit(main())
