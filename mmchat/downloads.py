"""Pure helpers for file downloads."""

from pathlib import Path
import re


_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def sanitize_filename(name: str, fallback: str = "download") -> str:
    """Return a filesystem-safe basename for a downloaded file."""
    cleaned = Path(name or "").name.strip()
    cleaned = cleaned.replace("/", "_").replace("\\", "_")
    cleaned = _CONTROL_CHARS.sub("", cleaned)
    cleaned = cleaned.strip(" .")
    return cleaned or fallback


def unique_download_path(directory: Path, filename: str) -> Path:
    """Return a non-clobbering path inside directory."""
    safe_name = sanitize_filename(filename)
    candidate = directory / safe_name
    if not candidate.exists():
        return candidate

    suffix = "".join(candidate.suffixes)
    stem = candidate.name[: -len(suffix)] if suffix else candidate.name
    counter = 1
    while True:
        candidate = directory / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def file_entries(post: dict) -> list[dict]:
    """Extract stable file metadata entries from a Mattermost post."""
    file_ids = post.get("file_ids") or []
    meta_files = post.get("metadata", {}).get("files") or []

    entries = []
    for idx, file_id in enumerate(file_ids):
        meta = meta_files[idx] if idx < len(meta_files) else {}
        entries.append({
            "id": file_id,
            "name": meta.get("name", ""),
            "size": meta.get("size", 0),
            "mime_type": meta.get("mime_type", ""),
            "extension": meta.get("extension", ""),
        })
    return entries


def download_record(file_id: str, metadata: dict, saved_to: Path) -> dict:
    """Build a JSON-friendly record for a downloaded file."""
    return {
        "file_id": file_id,
        "name": metadata.get("name", ""),
        "size": metadata.get("size", 0),
        "mime_type": metadata.get("mime_type", ""),
        "saved_to": str(saved_to),
    }
