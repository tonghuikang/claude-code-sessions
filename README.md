# Claude Code Conversation Visualizer

A web-based visualizer for browsing Claude Code conversation history.

## Setup

1. Sync conversation data:

```bash
./sync.sh
```

2. For local development, start the server:

```bash
uv run python server.py
```

Then open http://localhost:8080

## Static Hosting (GitHub Pages)

1. Run `./sync.sh` to sync data and build the index
2. Commit and push `data/` folder to your repository
3. Enable GitHub Pages in repository settings

