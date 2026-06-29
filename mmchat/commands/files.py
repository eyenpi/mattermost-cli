"""File download commands."""

import sys
from pathlib import Path

import click

from ..cli import get_context, main, pass_state
from ..client import EXIT_ERROR
from ..downloads import download_record, sanitize_filename, unique_download_path
from ..formatters import format_downloads_json, format_downloads_md


@main.command()
@click.argument("file_ids", nargs=-1, required=True)
@click.option(
    "--output",
    "output_dir",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Directory to save downloaded files.",
)
@pass_state
def download(state, file_ids, output_dir):
    """Download one or more attached files by file ID."""
    ctx = get_context(state)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        click.echo(f"Error: Could not create output directory '{output_dir}': {e}", err=True)
        sys.exit(EXIT_ERROR)

    results = []
    for file_id in file_ids:
        try:
            metadata = ctx.driver.files.get_file_metadata(file_id)
            response = ctx.driver.client.make_request("get", f"/files/{file_id}")
        except Exception as e:
            click.echo(f"Error: Could not download file '{file_id}': {e}", err=True)
            sys.exit(EXIT_ERROR)

        filename = sanitize_filename(metadata.get("name", "") or file_id, fallback=file_id)
        destination = unique_download_path(output_dir, filename)
        destination.write_bytes(response.content)
        results.append(download_record(file_id, metadata, destination))

    if not state.human:
        click.echo(format_downloads_json(results))
    else:
        click.echo(format_downloads_md(results))
