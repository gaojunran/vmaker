from pathlib import Path
from datetime import datetime
import rich
from rich.console import Console
from rich.table import Table


def print_videos_info(videos: list[Path]):
	table = Table()
	table.add_column("Name", justify="right", style="cyan", no_wrap=True)
	table.add_column("Datetime", justify="right", style="magenta")
	table.add_column("Length(H:S:M)", justify="right", style="green")
	table.add_column("Size(MB)", justify="right", style="green")
	for video in videos:
		video: Path
		table.add_row(
			video.name,
			datetime.fromtimestamp(video.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
			"TODO",
			str(round(video.stat().st_size / 1024 / 1024, 2)),
		)
	console = Console()
	console.print(table)

def get_latest_video(dir: Path):
	all_files = list(dir.glob('**/*'))
	video_files = [file for file in all_files if file.suffix in ['.mp4', '.mkv']]
	return max(video_files, key=lambda file: file.stat().st_mtime)