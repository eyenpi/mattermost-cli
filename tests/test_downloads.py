"""Tests for pure download helpers."""

from mmchat.downloads import download_record, file_entries, sanitize_filename, unique_download_path


class TestSanitizeFilename:
    def test_strips_path_components(self):
        assert sanitize_filename("../../secret/report.pdf") == "report.pdf"

    def test_fallback_when_empty(self):
        assert sanitize_filename("   ", fallback="file-1") == "file-1"


class TestUniqueDownloadPath:
    def test_returns_original_name_when_free(self, tmp_path):
        path = unique_download_path(tmp_path, "report.pdf")
        assert path.name == "report.pdf"

    def test_appends_counter_on_conflict(self, tmp_path):
        (tmp_path / "report.pdf").write_text("x")
        path = unique_download_path(tmp_path, "report.pdf")
        assert path.name == "report-1.pdf"


class TestFileEntries:
    def test_pairs_ids_with_metadata(self):
        post = {
            "file_ids": ["f1", "f2"],
            "metadata": {
                "files": [
                    {"name": "one.txt", "size": 1, "mime_type": "text/plain", "extension": "txt"},
                    {"name": "two.txt", "size": 2, "mime_type": "text/plain", "extension": "txt"},
                ]
            },
        }
        assert file_entries(post) == [
            {"id": "f1", "name": "one.txt", "size": 1, "mime_type": "text/plain", "extension": "txt"},
            {"id": "f2", "name": "two.txt", "size": 2, "mime_type": "text/plain", "extension": "txt"},
        ]

    def test_handles_missing_metadata(self):
        post = {"file_ids": ["f1"]}
        assert file_entries(post) == [
            {"id": "f1", "name": "", "size": 0, "mime_type": "", "extension": ""},
        ]


class TestDownloadRecord:
    def test_builds_json_friendly_record(self, tmp_path):
        record = download_record("f1", {"name": "report.pdf", "size": 42, "mime_type": "application/pdf"}, tmp_path / "report.pdf")
        assert record == {
            "file_id": "f1",
            "name": "report.pdf",
            "size": 42,
            "mime_type": "application/pdf",
            "saved_to": str(tmp_path / "report.pdf"),
        }
