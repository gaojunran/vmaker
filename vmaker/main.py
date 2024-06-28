from pathlib import Path
from typing import Annotated

import typer
import rich
from rich.prompt import Prompt

from vmaker.constants import Actions
from vmaker.utils import print_videos_info, get_latest_video

app = typer.Typer()

SOURCE_DIR = r"C:\Users\nebul\Videos"
SOURCE_PATH = Path(SOURCE_DIR)
DEST_DIR = r"D:\_WORKS\_video\01"
DEST_PATH = Path(DEST_DIR)


@app.callback()
def callback():
	"""
    A tutorial video maker for programmers. With the help of Typer and ffmpeg.
    """
	pass


@app.command()
def add(
		new_name: Annotated[str, typer.Argument(help="The new name of the video.")] = Actions.DONT_RENAME,
):
	"""
	Add the latest recorded video to the predetermined folder.
	"""
	video = get_latest_video(SOURCE_PATH)
	suffix = video.suffix
	rich.print(f"Will copy the video below to [green]{DEST_DIR}[/green] with the new name [green]{new_name}{suffix}[/green]. ")
	print_videos_info([video])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		print("Success!")

@app.command()
def dir():
	"""
	Show source directory, destination directory and video output directory.
	"""
	rich.print(f"[green]Source Dir[/green]: [link=file:///{SOURCE_DIR}]{SOURCE_DIR}[/link]")
	rich.print(f"[green]Destination Dir[/green]: [link=file:///{DEST_DIR}]{DEST_DIR}[/link]")
