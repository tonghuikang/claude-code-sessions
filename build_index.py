#!/usr/bin/env python3
"""Build index.json for static hosting of the visualizer."""

import json
import os
from pathlib import Path


def get_conversation_metadata(file_path: Path) -> dict:
    """Extract metadata from JSONL file."""
    result = {
        "summary": "",
        "parentSessionId": None,
        "agentId": None,
        "firstUserMessage": "",
    }
    try:
        with open(file_path) as f:
            for line in f:
                data = json.loads(line)
                if data.get("type") == "summary":
                    result["summary"] = data.get("summary", "")
                # For agent sessions, extract parent session and agent ID
                if data.get("agentId") and not result["agentId"]:
                    result["agentId"] = data.get("agentId")
                    result["parentSessionId"] = data.get("sessionId")
                # Extract first real user message (not tool results, not meta/system messages)
                if (
                    data.get("type") == "user"
                    and not result["firstUserMessage"]
                    and data.get("message")
                    and not data.get(
                        "isMeta"
                    )  # Skip meta messages (hook feedback, etc)
                ):
                    content = data["message"].get("content", "")
                    # Skip tool results (array with tool_result items)
                    if isinstance(content, list):
                        continue
                    # Skip internal warmup messages
                    if content == "Warmup":
                        continue
                    # Skip continuation messages from context overflow
                    if isinstance(content, str) and content.startswith(
                        "This session is being continued from a previous conversation"
                    ):
                        continue
                    if isinstance(content, str) and content.strip():
                        result["firstUserMessage"] = content[:100]
                # Stop once we have what we need
                if result["summary"] and result["firstUserMessage"]:
                    break
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass
    return result


def get_conversation_summary(file_path: Path) -> str:
    """Extract summary from first line of JSONL file."""
    return get_conversation_metadata(file_path).get("summary", "")


def build_index(data_dir: Path) -> dict:
    """Build index of all projects and sessions."""
    projects = []

    if not data_dir.exists():
        return {"projects": projects}

    for item in sorted(data_dir.iterdir()):
        if not item.is_dir():
            continue

        sessions = []
        try:
            for jsonl_file in sorted(
                item.glob("*.jsonl"), key=os.path.getmtime, reverse=True
            ):
                metadata = get_conversation_metadata(jsonl_file)
                # Use path relative to repo root (includes data/)
                session_entry = {
                    "name": jsonl_file.name,
                    "path": str(jsonl_file.relative_to(data_dir.parent.parent)),
                    "summary": metadata["summary"],
                    "firstUserMessage": metadata["firstUserMessage"],
                    "modified": os.path.getmtime(jsonl_file),
                }
                # Add agent-specific fields if present
                if metadata["agentId"]:
                    session_entry["agentId"] = metadata["agentId"]
                    session_entry["parentSessionId"] = metadata["parentSessionId"]
                sessions.append(session_entry)
        except OSError:
            continue

        if sessions:
            projects.append(
                {
                    "name": item.name,
                    "path": str(item.relative_to(data_dir.parent.parent)),
                    "sessionCount": len(sessions),
                    "sessions": sessions,
                }
            )

    return {"projects": projects}


def main():
    data_dir = Path(__file__).parent / "data" / "projects"
    output_file = Path(__file__).parent / "data" / "index.json"

    index = build_index(data_dir)

    # Ensure data directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(index, f, indent=2)

    print(f"Built index with {len(index['projects'])} projects")
    total_sessions = sum(p["sessionCount"] for p in index["projects"])
    print(f"Total sessions: {total_sessions}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
