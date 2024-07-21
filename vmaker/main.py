import json
import os
import re
from pathlib import Path
from typing import Annotated

import questionary
from asker import ask

import rich
import typer
from questionary import select, text
from rich.prompt import Prompt

from vmaker.constants import Lists, RenameStrategies
from vmaker.funcs import copy, ffmpeg_cut, ffmpeg_mute
from vmaker.utils import print_videos_info, get_latest_videos, count_videos, throw, \
	get_video_from_name, file_backup, is_valid_path, list_dir, inplace
from vmaker.config import Config

app = typer.Typer()

CWD = Path.cwd()


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
	If you just want `curr_path` to be changed, run `vmaker curr [...]` instead.
	"""

	raw_dir = text("Enter path as `raw_dir`", instruction="The path where recorded videos are saved \n").ask()
	clip_dir = text("Enter path as `clip_dir` ",
					instruction="The path where clips are saved once running `vmaker add` \n",
					default=f"{CWD / 'video_clip'}").ask()
	output_dir = text("Enter path as `output_dir`",
					  instruction="The path where output videos are saved \n",
					  default=f"{CWD / 'video_output'}").ask()
	curr_dir_backup_choices = list_dir(Path(clip_dir), only_dir=True, return_name=True) + ["[Create New Directory...]"]
	curr_dirname = select("Choose a working directory", instruction="Here lists all the folders inside `clip_dir`",
						  choices=curr_dir_backup_choices).ask()
	if curr_dirname == "[Create New Directory...]":
		curr_dirname = text("The name of the new directory \n").ask()
	Config.dump(Config(raw_dir, clip_dir, output_dir, curr_dirname))
	typer.echo("Success! If it still doesn't work well, please reboot the terminal.")


@app.command()
def curr(
		dir_name: Annotated[str, typer.Argument(help="The directory name to be set as current.")] = "",
):
	"""
	Set up the current working directory in `clip_dir`.
	The directory will be created if it doesn't exist.
	"""
	config = Config.load()
	if not dir_name:
		curr_dir_backup_choices = list_dir(config.clip_path, only_dir=True, return_name=True) + [
			"[Create New Directory...]"]
		curr_dirname = select("Choose a working directory", instruction="Here lists all the folders inside `clip_dir`",
							  choices=curr_dir_backup_choices).ask()
		if curr_dirname == "[Create New Directory...]":
			curr_dirname = text("The name of the new directory \n").ask()
		Config.dump(config.with_curr_dirname(curr_dirname))
	else:
		Config.dump(config.with_curr_dirname(dir_name))
	typer.echo("Success! If it still doesn't work well, please reboot the terminal.")


@app.command()
def add(
		new_name: Annotated[str, typer.Argument(help="The new name of the video.")] = "",
		choose: Annotated[bool, typer.Option("--choose", "-c", help="Choose the video to add.")] = False,
		rename_strategy: Annotated[int, typer.Option("--rename", "-r",
													 help="Rename strategy only available when new_name is not given. See the doc for more choices.")] = RenameStrategies.DONT_RENAME
):
	"""
	Add the latest recorded video to the clip folder.
	"""
	config = Config.load()
	if not choose:
		video = get_latest_videos(config.raw_path)[0]
	else:
		choices = get_latest_videos(config.raw_path, 6)
		print_videos_info(choices)
		index = Prompt.ask("Choose one from above: ", choices=["0", "1", "2", "3", "4", "5"], default="0")
		video = choices[int(index)]
	suffix = video.suffix

	if not new_name:
		if rename_strategy == RenameStrategies.DONT_RENAME:
			final_name = video.name
	# elif rename_strategy == RenameStrategies.RENAME_WITH_TIME:
	# 	final_name = video.stem + "_" + video.stat().st_mtime + suffix
	else:
		final_name = new_name + suffix

	rich.print(
		f"Will copy the video below to [green]{str(config.curr_path)}[/green] with the new name [green]{final_name}[/green]. ")
	print_videos_info([video])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		# action
		copy(video, config.curr_path / final_name)
		rich.print("[bold green]Success![/bold green]")
		count_videos(config.curr_path)


@app.command()
def rm(
		clip_name: Annotated[str, typer.Argument(help="The video name to remove.")] = "",
):
	"""
	Remove the latest clip(by default) or a specified clip.
	"""
	config = Config.load()
	if not clip_name:
		rm_path = get_latest_videos(config.curr_path) and config.curr_path / get_latest_videos(config.curr_path)[0]
	else:
		rm_path = get_video_from_name(clip_name, config.curr_path)

	if not rm_path:
		throw("finding the latest video", "No clip to remove.")

	if not rm_path.exists():
		throw("removing", f"The file {rm_path} does not exist.")

	rich.print(
		f"Will remove the video below: ")
	print_videos_info([rm_path])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		# action
		Path(rm_path).unlink()
		rich.print("[bold green]Success![/bold green]")
		count_videos(config.curr_path)
	Path(rm_path).unlink()


@app.command()
def cut(
		clip_name: Annotated[str, typer.Argument(help="The video name to be cut.")],
		start_time: Annotated[
			str, typer.Argument(help="format: 01:02:03 for 1 hour 2 minutes 3 seconds.")],
		end_time: Annotated[str, typer.Argument(help="format: 01:02:03 for 1 hour 2 minutes 3 seconds.")],
		rename_strategy: Annotated[int, typer.Option("--rename", "-r",
													 help="Rename strategy. See the doc for more choices.")] = RenameStrategies.RENAME_WITH_SUFFIX,
		is_keep: Annotated[bool, typer.Option("--keep", "-k", help="Keep the original video or not.")] = False,
		is_backup: Annotated[bool, typer.Option("--backup", "-b", help="Backup the original video or not.")] = True,
):
	"""
	Cut a video by given start and end time.
	"""
	config = Config.load()
	if not (re.match(r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$", start_time) and re.match(r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$",
																			   end_time)):
		throw("checking parameters", "Invalid time format. Correct format: `01:02:03`. ")

	clip_input = get_video_from_name(clip_name, config.curr_path)
	rich.print(
		f"Will cut the video below from [green]{start_time}[/green] to [green]{end_time}[/green]. ")
	print_videos_info([clip_input])
	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
	if choice == "Y":
		# action
		if rename_strategy == RenameStrategies.RENAME_WITH_SUFFIX:
			is_backup and file_backup(clip_input, config.curr_path)
			ffmpeg_cut(clip_input, start_time, end_time, clip_input.with_stem(clip_input.stem + "_cut"))
		rich.print("[bold green]Success![/bold green]")
	is_keep or clip_input.unlink()


# @app.command()
# def music(
# 		clip_name: Annotated[str, typer.Argument(help="The video name to be operated.")],
# 		music: Annotated[str, typer.Argument(help="The music file path.")],
# 		is_mute: Annotated[bool, typer.Option("--mute", "-m", help="Mute the original audio or not.")] = False,
# 		rename_strategy: Annotated[int, typer.Option("--rename", "-r",
# 													 help="Rename strategy. See the doc for more choices.")] = RenameStrategies.RENAME_WITH_SUFFIX,
# 		is_keep: Annotated[bool, typer.Option("--keep", "-k", help="Keep the original video or not.")] = False,
# 		is_backup: Annotated[bool, typer.Option("--backup", "-b", help="Backup the original video or not.")] = True,
# ):
# 	"""
# 	Add background music to a video.
# 	"""
#
# 	is_valid_path(music) or throw("checking parameters", f"Invalid music file path {music}.")
# 	clip_input = get_video_from_name(clip_name, CLIP_PATH)
# 	rich.print(
# 		f"Will add music [green]{music}[/green] to the video below. ")
# 	print_videos_info([clip_input])
# 	is_mute and rich.print("[blue]Will MUTE the original audio.[/blue]")
# 	is_keep or rich.print("[blue]Will NOT keep the original video file.[/blue]")
# 	is_backup and rich.print("[blue]Will back up the original video file.[/blue]")
# 	choice = Prompt.ask("Sure to continue?", choices=["Y", "n"], default="Y")
# 	if choice == "Y":
# 		# action
# 		if rename_strategy == RenameStrategies.RENAME_WITH_SUFFIX:
# 			is_backup and file_backup(clip_input, CLIP_PATH)
# 			is_mute and ffmpeg_mute(clip_input, clip_input.with_stem(clip_input.stem + "_mute"))
# 			ffmpeg_music(clip_input, clip_input.with_stem(clip_input.stem + "_music"))
# 		rich.print("[bold green]Success![/bold green]")
# 	is_keep or clip_input.unlink()

@app.command()
def mute(
		clip_name: Annotated[str, typer.Argument(help="The video name to be operated.")],
		is_backup: Annotated[bool, typer.Option("--backup", "-b", help="Backup the original video or not.")] = True,
):
	config = Config.load()
	clip_input = get_video_from_name(clip_name, config.curr_path)
	ffmpeg_mute(
		clip_input,
		clip_input.with_stem(clip_input.stem + "_output")
	)
	inplace(clip_input, is_backup)


@app.command()
def cfg():
	"""
	Show configs.
	"""
	config = Config.load()
	typer.echo(config)
