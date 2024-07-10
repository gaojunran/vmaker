import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import rich
from rich.console import Console
from rich.table import Table

from vmaker.constants import Lists


def is_valid_path(s):
	try:
		return Path(s).exists()
	except OSError:
		return False

def get_valid_path(s):
	if is_valid_path(s):
		return Path(s)
	else:
		throw(f"resolving path", f"{s} is not a valid path.")

def check_config_exists():
	config = json.loads(os.getenv("VMAKER_CONFIG")) if os.getenv("VMAKER_CONFIG") else {}
	return all(config.get(key) for key in Lists.CONFIG_LIST)


def print_videos_info(videos: list[Path]):
	table = Table()
	table.add_column("Idx", justify="right", style="dim")
	table.add_column("Name", justify="right", style="cyan", no_wrap=True)
	table.add_column("Datetime", justify="right", style="magenta")
	table.add_column("Length(H:S:M)", justify="right", style="green")
	table.add_column("Size(MB)", justify="right", style="green")
	for idx, video in enumerate(videos):
		video: Path
		table.add_row(
			str(idx),
			video.name,
			datetime.fromtimestamp(video.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
			"TODO",
			str(round(video.stat().st_size / 1024 / 1024, 2)),
		)
	console = Console()
	console.print(table)


def get_latest_videos(dir: Path, num=1):
	all_files = list(dir.glob('**/*'))
	video_files = [file for file in all_files if file.suffix in ['.mp4', '.mkv']]
	return sorted(video_files, key=lambda file: file.stat().st_mtime)[:num]


def get_video_from_name(name: str, dir: Path) -> Path | None:

	for file in dir.iterdir():
		number = file.split('-')[0]
		if file.suffix in Lists.VIDEO_EXTS and (file.stem == name or number == name):
			return file
	else:
		throw("finding the video to be cut", f"Video {name} not found.")


def count_videos(dir: Path):
	all_files = list(dir.glob('**/*'))
	count = len([file for file in all_files if file.suffix in Lists.VIDEO_EXTS])
	rich.print(f"Now you have [green]{count}[/green] videos in {dir}.")


def file_backup(file: Path, backup_dir: Path = None):
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	if backup_dir:
		backup_file = backup_dir / (file.name + "_" + timestamp + '.bak')
	else:
		backup_file = file.with_name(file.name + "_" + timestamp + '.bak')
	try:
		backup_file.write_bytes(file.read_bytes())
	except Exception as e:
		throw(f"backing up the file {file.name}", str(e))


def throw(situation: str, detail: str):
	err_console = Console(stderr=True, style="bold red")
	err_console.print(f"An error occurred when {situation}: \n{detail}")
	sys.exit()
