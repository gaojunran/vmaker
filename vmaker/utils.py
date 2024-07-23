import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

import questionary
import rich
from rich.console import Console
from rich.table import Table

from vmaker.constants import Lists



def to_hsm(seconds):
	"""
	Convert seconds to a formatted string in the format of HH:MM:SS.

	:param seconds: Total number of seconds
	:return: Formatted time string
	"""
	hours = seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = seconds % 60
	return f"{hours:02}:{minutes:02}:{seconds:02}"

def succeed_operation(
	dir: Path
):
	rich.print("\n\n[bold green]Success![/bold green]")
	if platform.system() == "Windows":
		command_line = f"explorer \"{str(dir)}\""
		choice = questionary.confirm("Check the videos in Explorer?").ask()
		choice and os.system(command_line)
	elif platform.system() == "Linux":
		command_line = f"xdg-open \"{str(dir)}\""
		choice = questionary.confirm("Check the videos in File Manager?").ask()
		choice and os.system(command_line)
	elif platform.system() == "Darwin":
		command_line = f"open \"{str(dir)}\""
		choice = questionary.confirm("Check the videos in Finder?").ask()
		choice and os.system(command_line)

def confirm_operation(
		prompt: str,
		operated_files: list[Path],
):
	rich.print(prompt)
	print_videos_info(operated_files)
	choice = questionary.confirm("Sure to continue? After your choice, please wait until an explicit `Success!`.").ask()
	return choice

def inplace(
		operated_file: Path,
		is_backup: bool = True
):
	"""
	By default, all actions which edit ONE video returns a video with a suffix "_output",
	This function alters this behaviour by the following steps:
	- removing the raw video, and keeping it if needed.
	- renaming the new video.
	"""
	name = operated_file.name  # video.mp4
	if is_backup:
		file_backup(operated_file)
	operated_file.unlink()
	# find a backup video based on its name
	new_video = get_video_from_name(name, operated_file.parent)
	new_video.rename(operated_file.parent / new_video.name.replace("_output", ""))


def list_dir(dir: Path,
			 only_file=False,
			 only_dir=False,
			 return_name=False
			 ):
	if only_file and only_dir:
		raise ValueError("only_file and only_dir cannot both be True")

	def generator():
		for p in dir.iterdir():
			p: Path
			if (only_file and p.is_dir()) or (only_dir and p.is_file()):
				continue
			yield p.name if return_name else p

	return list(generator())


def is_valid_path(s, allow_not_exist=False):
	try:
		if allow_not_exist:
			Path(s).mkdir(parents=True, exist_ok=True)
			return True
		else:
			return Path(s).exists()
	except OSError:
		return False


def get_valid_path(s, allow_not_exist=False):
	if is_valid_path(s, allow_not_exist):
		return Path(s)
	else:
		throw(f"resolving path", f"{s} is not a valid path.")


def print_videos_info(videos: list[Path]):
	from vmaker.funcs import ffprobe_duration
	table = Table()
	table.add_column("Idx", justify="right", style="dim")
	table.add_column("Name", justify="right", style="cyan", no_wrap=True)
	table.add_column("Datetime", justify="right", style="magenta")
	table.add_column("Duration(H:S:M)", justify="right", style="green")
	table.add_column("Size(MB)", justify="right", style="green")
	for idx, video in enumerate(videos):
		video: Path
		table.add_row(
			str(idx),
			video.name,
			datetime.fromtimestamp(video.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
			to_hsm(ffprobe_duration(video)),
			str(round(video.stat().st_size / 1024 / 1024, 2)),
		)
	console = Console()
	console.print(table)


def get_latest_videos(dir: Path, num=1):
	all_files = list(dir.glob('**/*'))
	video_files = [file for file in all_files if file.suffix in ['.mp4', '.mkv']]
	return sorted(video_files, key=lambda file: file.stat().st_mtime, reverse=True)[:num]


def get_video_from_name(name: str, dir: Path) -> Path | None:
	for file in dir.iterdir():
		number = file.stem.split('-')[0] if '-' in file.name else None
		# find the file "example.mp4" by the name "example"
		if file.suffix in Lists.VIDEO_EXTS and (file.stem == name or number == name):
			return file
		# find the backup file "example_output.mp4" by the name "example.mp4"
		elif "_output" in file.name and name.split(".")[0] in file.name:
			return file
	else:
		throw("finding the video", f"Video {name} not found.")


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


if __name__ == '__main__':
	print(Path(r"D:\video.mp4.output").stem)
