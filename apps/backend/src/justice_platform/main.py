"""CLI entrypoint for local execution."""

from __future__ import annotations

import uvicorn

from .app import get_app


def main() -> None:
    """Run a development server using uvicorn."""

    uvicorn.run(
        "justice_platform.app:get_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
