#!/usr/bin/env python3
"""Simple server to browse Claude Code conversation history."""

import http.server
import json
import os
import socketserver
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEFAULT_PORT = 44043
DATA_DIR = Path(__file__).parent / "data" / "projects"


def find_available_port(start_port: int, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            continue
    raise RuntimeError(
        f"No available port found in range {start_port}-{start_port + max_attempts}"
    )


class ConversationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/projects":
            self.send_projects_list()
        elif parsed.path == "/api/sessions":
            query = parse_qs(parsed.query)
            project = query.get("project", [""])[0]
            self.send_sessions_list(project)
        elif parsed.path == "/api/conversation":
            query = parse_qs(parsed.query)
            file_path = query.get("file", [""])[0]
            self.send_conversation(file_path)
        else:
            super().do_GET()

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_projects_list(self):
        projects = []
        if DATA_DIR.exists():
            for item in sorted(DATA_DIR.iterdir()):
                if item.is_dir():
                    # Count jsonl files efficiently using os.listdir
                    try:
                        files = os.listdir(item)
                        session_count = sum(1 for f in files if f.endswith(".jsonl"))
                        if session_count > 0:
                            projects.append(
                                {
                                    "name": item.name,
                                    "path": str(item),
                                    "sessionCount": session_count,
                                }
                            )
                    except OSError:
                        pass
        self.send_json(projects)

    def send_sessions_list(self, project):
        sessions = []
        project_path = DATA_DIR / project
        if project_path.exists():
            for item in sorted(
                project_path.glob("*.jsonl"), key=os.path.getmtime, reverse=True
            ):
                summary = self.get_conversation_summary(item)
                sessions.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "summary": summary,
                        "modified": os.path.getmtime(item),
                    }
                )
        self.send_json(sessions)

    def get_conversation_summary(self, file_path):
        try:
            with open(file_path) as f:
                first_line = f.readline()
                data = json.loads(first_line)
                if data.get("type") == "summary":
                    return data.get("summary", "")
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            pass
        return ""

    def send_conversation(self, file_path):
        try:
            with open(file_path) as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404, "File not found")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    port = find_available_port(DEFAULT_PORT)
    with socketserver.TCPServer(("", port), ConversationHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print(f"Open http://localhost:{port}")
        httpd.serve_forever()
