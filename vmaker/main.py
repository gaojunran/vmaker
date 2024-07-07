import json
import os
import re
import sys
from pathlib import Path
from typing import Annotated

import typer
import rich
from rich.console import Console
from rich.prompt import Prompt

from vmaker.constants import RenameActions, Lists, RenameStrategies
from vmaker.funcs import copy
from vmaker.utils import print_videos_info, get_latest_videos, env_update, count_videos, throw, check_config

app = typer.Typer()

config = json.loads(os.getenv("VMAKER_CONFIG")) if os.getenv("VMAKER_CONFIG") else {}

RAW_DIR = config.get("raw_dir")
RAW_PATH = RAW_DIR and Path(RAW_DIR)
CLIP_DIR = config.get("clip_dir")
CLIP_PATH = CLIP_DIR and Path(CLIP_DIR)
OUTPUT_DIR = config.get("output_dir")
OUTPUT_PATH = OUTPUT_DIR and Path(OUTPUT_DIR)

CWD = Path.cwd()


# def throw_if_not_init():
# 	if not (RAW_DIR and CLIP_DIR and OUTPUT_DIR):
# 		err_console = Console(stderr=True, style="bold red")
# 		err_console.print("Please run `vmaker init` first.")
# 		sys.exit()


@app.callback()
def callback():
	"""
    A tutorial video maker for programmers. With the help of Typer and ffmpeg.
    """
	pass


@app.command()
def init():
	"""
	Config default settings for the first time.
	If you want one of them to be changed, run `vmaker config [...]` instead.
	"""
	raw_dir = RAW_DIR or Prompt.ask("The path where videos are recorded")
	clip_dir = CLIP_DIR or Prompt.ask("The path where clips are saved", default=f"{CWD / "clips"}")
	output_dir = OUTPUT_DIR or Prompt.ask("The path where final videos are saved",
										  default=f"{CWD / "output"}")
	env_update(raw_dir=raw_dir, clip_dir=clip_dir, output_dir=output_dir)
	typer.echo("Success! If it still doesn't work well, please reboot the terminal.")


def config():
	pass


@app.command()
def add(
		new_name: Annotated[str, typer.Argument(help="The new name of the video.")] = RenameActions.DONT_RENAME,
		choose: Annotated[bool, typer.Option("--choose", "-c", help="Choose the video to add.")] = False,
):
	"""
	Add the latest recorded video to the clip folder.
	"""
	check_config() or throw("adding", "Config missing. Please run `vmaker init` first.")
	if not choose:
		video = get_latest_videos(RAW_PATH)[0]
	else:
		choices = get_latest_videos(RAW_PATH, 6)
		print_videos_info(choices)
		index = Prompt.ask("Choose one from above: ", choices=["0", "1", "2", "3", "4", "5"], default="0")
		video = choices[int(index)]
	suffix = video.suffix

	if new_name == RenameActions.DONT_RENAME:
		final_name = video.name
	elif new_name == RenameActions.RENAME_WITH_TIME:
		final_name = video.stem + "_" + video.stat().st_mtime + suffix
	else:
		final_name = new_name + suffix

	rich.print(
		f"Will copy the video below to [green]{CLIP_DIR}[/green] with the new name [green]{final_name}[/green]. ")
	print_videos_info([video])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		# action
		copy(video, CLIP_PATH / final_name)
		rich.print("[bold green]Success![/bold green]")


@app.command()
def rm(
		clip_name: Annotated[str, typer.Argument(help="The video name to remove.")] = "",
):
	"""
	Remove the latest clip(by default) or a specified clip.
	"""

	if not clip_name:
		rm_path = get_latest_videos(CLIP_PATH) and CLIP_PATH / get_latest_videos(CLIP_PATH)[0]
	else:
		rm_path = CLIP_PATH / clip_name

	if not rm_path:
		throw("removing", "No clip to remove.")
		sys.exit()

	if not rm_path.exists():
		throw("removing", f"The file {rm_path} does not exist.")
		sys.exit()

	rich.print(
		f"Will remove the video below: ")
	print_videos_info([rm_path])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		# action
		Path(rm_path).unlink()
		rich.print("[bold green]Success![/bold green]")
		count_videos(CLIP_PATH)
	Path(rm_path).unlink()


@app.command()
def cut(
		clip_name: Annotated[str, typer.Argument(help="The video name to be cut")] = "",
		start_time: Annotated[str, typer.Argument(help="format: 01:02:03 for 1 hour 2 minutes 3 seconds.")] = "00:00:00",
		end_time: Annotated[str, typer.Argument(help="format: 01:02:03 for 1 hour 2 minutes 3 seconds.")] = "00:00:00",
		rename_strategy: Annotated[int, typer.Option("--rename", "-r", help="Rename strategy. See the doc for more choices.")] = RenameStrategies.DONT_RENAME
):
	"""
	Cut a video by given start and end time.
	"""
	if not (re.match(r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$", start_time) and re.match(r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$", end_time)):
		throw("cutting", "Invalid time format. Correct format: `01:02:03`. ")
	if rename_strategy == RenameStrategies.DONT_RENAME:






@app.command()
def list():
	"""
	Show configs.
	"""
	check_config() or throw("showing config", "Config missing. Please run `vmaker init` first.")
	for k, v in config.items():
		if k in Lists.DIR_CONFIG_LIST:
			rich.print(f"[green]{k}[/green]: [link=file:///{v}]{v}[/link]")
		else:
			rich.print(f"[green]{k}[/green]: {v}")
