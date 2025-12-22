For changes involving html files, please use MCP puppeteer to test.

Testing HTML changes
- ONLY use `./run_server.sh` - it handles everything (kills existing servers, starts new one)
- NEVER run `uv run python server.py` directly or any other server command - ONLY `./run_server.sh`
- NEVER use background execution (&) or nohup for starting servers
- NEVER run `lsof`, `kill`, or any port management commands - `./run_server.sh` handles this
- If server fails to start, just run `./run_server.sh` again - do NOT try to debug with other commands
- Test at http://localhost:44043/

Package Management
- ONLY use uv, NEVER pip
- Installation: uv add package
- Running tools: uv run tool
- Upgrading: uv add --dev package --upgrade-package package
- FORBIDDEN: uv pip install, @latest syntax

Formatting
- Format: uv run --frozen ruff format *.py
- Check: uv run --frozen ruff check *.py
- Fix: uv run --frozen ruff check *.py --fix
- Sort imports: uv run --frozen ruff check --select I *.py --fix
- Type checking: uv run --frozen mypy *.py

Cleanup
- You may be asked for a data privacy review. Follow these processes
    - Delete gitignored files (except .venv): `git clean -fdX -e .venv`
        - Run the full run, not the dry run
    - Search among existing files for private information
        - Example of private information
            - API keys
            - Contact information

Approved Commands
- ./run_server.sh
