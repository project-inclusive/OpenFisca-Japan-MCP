import argparse
import sys
from .server import mcp

def main():
    parser = argparse.ArgumentParser(description="OpenFisca-Japan MCP Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="Transport type to use for MCP. Default is stdio."
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080,
        help="Port to use for SSE server. Ignored if transport is stdio."
    )
    
    args = parser.parse_args()
    
    if args.transport == "sse":
        # Launch using SSE transport
        print(f"Starting OpenFisca-Japan-MCP on SSE port {args.port}...")
        mcp.run(transport="sse", port=args.port)
    else:
        # Launch using standard input/output
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
