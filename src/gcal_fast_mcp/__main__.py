"""Entry point: uv run python -m gcal_fast_mcp"""

import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        from gcal_fast_mcp.auth import authenticate

        redirect_uri = sys.argv[2] if len(sys.argv) > 2 else None
        authenticate(redirect_uri)
        return

    from gcal_fast_mcp.server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
