import json
import os
import platform
import subprocess
from pathlib import Path
from datetime import datetime
import rich
from rich.console import Console
from rich.table import Table



def env_init(raw_dir, clip_dir, output_dir):
	_set_env_var("VMAKER_RAW_DIR", raw_dir)
	_set_env_var("VMAKER_CLIP_DIR", clip_dir)
	_set_env_var("VMAKER_OUTPUT_DIR", output_dir)


def _set_env_var(name, value):
	system = platform.system()
	if system == 'Windows':
		# 设置Windows环境变量
		subprocess.run(['setx', name, value], shell=True)
	elif system in ('Linux', 'Darwin'):  # Darwin表示macOS
		# 设置Linux或macOS环境变量
		shell_config_file = os.path.expanduser('~/.bashrc')
		with open(shell_config_file, 'a') as file:
			file.write(f'\nexport {name}={value}\n')
		print(f'Run `source {shell_config_file}` to make the changes effective.')
	else:
		raise NotImplementedError(f'Unsupported platform: {system}')


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


def get_latest_video(dir: Path, num=1):
	all_files = list(dir.glob('**/*'))
	video_files = [file for file in all_files if file.suffix in ['.mp4', '.mkv']]
	return sorted(video_files, key=lambda file: file.stat().st_mtime)[:num]
