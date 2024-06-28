import os
import sys
from pathlib import Path
from typing import Annotated

import typer
import rich
from rich.console import Console
from rich.prompt import Prompt

from vmaker.constants import Actions
from vmaker.utils import print_videos_info, get_latest_video, env_init

app = typer.Typer()

RAW_DIR = os.getenv("VMAKER_RAW_DIR")
RAW_PATH = RAW_DIR and Path(RAW_DIR)
CLIP_DIR = os.getenv("VMAKER_CLIP_DIR")
CLIP_PATH = CLIP_DIR and Path(CLIP_DIR)
OUTPUT_DIR = os.getenv("VMAKER_OUTPUT_DIR")
OUTPUT_PATH = OUTPUT_DIR and Path(OUTPUT_DIR)

CWD = Path.cwd()

def throw_if_not_init():
	if not (RAW_DIR and CLIP_DIR and OUTPUT_DIR):
		err_console = Console(stderr=True, style="bold red")
		err_console.print("Please run `vmaker init` first.")
		sys.exit()


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
	raw_dir = os.getenv("VMAKER_RAW_DIR") or Prompt.ask("The path where videos are recorded")
	clip_dir = os.getenv("VMAKER_CLIP_DIR") or Prompt.ask("The path where clips are saved", default=f"{CWD / "clips"}")
	output_dir = os.getenv("VMAKER_OUTPUT_DIR") or Prompt.ask("The path where final videos are saved", default=f"{CWD / "output"}")
	env_init(raw_dir, clip_dir, output_dir)
	typer.echo("Success! If it still doesn't work well, please reboot the terminal.")


def config():
	pass

@app.command()
def add(
		new_name: Annotated[str, typer.Argument(help="The new name of the video.")] = Actions.DONT_RENAME,
		choose: Annotated[bool, typer.Option("--choose", "-c", help="Choose the video to add.")] = False,
):
	"""
	Add the latest recorded video to the clip folder.
	"""
	throw_if_not_init()
	if not choose:
		video = get_latest_video(RAW_PATH)
	else:
		choices = get_latest_video(RAW_PATH, 6)
		print_videos_info(choices)
		index = Prompt.ask("Choose one from above: ", choices=["0", "1", "2", "3", "4", "5"], default="0")
		video = choices[int(index)]
	suffix = video.suffix
	rich.print(
		f"Will copy the video below to [green]{CLIP_DIR}[/green] with the new name [green]{new_name}{suffix}[/green]. ")
	print_videos_info([video])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		print("Success!")


@app.command()
def dir():
	"""
	Show source directory, destination directory and video output directory.
	"""
	throw_if_not_init()
	rich.print(f"[green]RAW Dir[/green]: [link=file:///{RAW_DIR}]{RAW_DIR}[/link]")
	rich.print(f"[green]CLIP Dir[/green]: [link=file:///{CLIP_DIR}]{CLIP_DIR}[/link]")
	rich.print(f"[green]OUTPUT Dir[/green]: [link=file:///{OUTPUT_DIR}]{OUTPUT_DIR}[/link]")
