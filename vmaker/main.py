import re
from pathlib import Path
from typing import Annotated, List

import questionary
import rich
import typer
from questionary import select, text

from vmaker.config import Config
from vmaker.constants import Lists, RenameStrategies
from vmaker.funcs import copy, ffmpeg_cut, ffmpeg_mute, ffmpeg_convert, ffmpeg_speed, ffprobe_duration
from vmaker.utils import print_videos_info, get_latest_videos, count_videos, throw, \
	get_video_from_name, list_dir, inplace, confirm_operation, succeed_operation, to_hsm

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
	typer.echo("Success! If it still doesn't work well, please restart the terminal.")


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
		choices = get_latest_videos(config.raw_path, 20)
		print_videos_info(choices)
		index = questionary.text("Enter the Idx to choose: ").ask()
		video = choices[int(index)]
	suffix = video.suffix

	if not new_name:
		new_name = questionary.text(
			"Do you forget to give the clip a new name? Input a new name or just enter to avoid renaming. \n").ask()
		if not new_name and rename_strategy == RenameStrategies.DONT_RENAME:
			final_name = video.name
	# elif rename_strategy == RenameStrategies.RENAME_WITH_TIME:
	# 	final_name = video.stem + "_" + video.stat().st_mtime + suffix
		else:
			final_name = new_name + suffix

	rich.print(
		f"Will copy the video below to [green]{str(config.curr_path)}[/green] with the new name [green]{final_name}[/green]. ")
	print_videos_info([video])
	if questionary.confirm("Sure to continue? After your choice, please wait until an explicit `Success!`.").ask():
		# action
		copy(video, config.curr_path / final_name)
		rich.print("[bold green]Success![/bold green]")
		count_videos(config.curr_path)


@app.command()
def convert(
		clip_name: Annotated[str, typer.Argument(help="The video name to be converted.")] = None,
		suffix: Annotated[str, typer.Argument(help="The suffix of the converted video, such as `.mkv`.")] = ".mp4",
		many: Annotated[List[str], typer.Option("--many", "-m",
												help="Convert multiple videos at once, give clip_names separated by space.")] = None,
		is_backup: Annotated[bool, typer.Option("--backup", "-b", help="Backup the original video or not.")] = True,
):
	config = Config.load()
	if many and not clip_name:
		clip_inputs = [get_video_from_name(video, config.curr_path) for video in many]
	elif clip_name and not many:
		clip_inputs = [get_video_from_name(clip_name, config.curr_path)]
	else:
		throw("checking parameters", "Please give either `clip_name` or `many`. Giving both is not allowed.")
	if confirm_operation(f"Will convert the following video(s) to [bold green]{suffix}[/bold green]:", clip_inputs):
		for video in clip_inputs:
			ffmpeg_convert(
				video,
				video.with_name(video.stem + "_output" + suffix)
			)
			inplace(video, is_backup)
		succeed_operation(config.curr_path)


@app.command()
def rm(
		clip_names: Annotated[List[str], typer.Argument(help="The video names to remove.")],
):
	"""
	Remove given clip(s).
	"""
	config = Config.load()
	rm_paths = [get_video_from_name(video, config.curr_path) for video in clip_names]

	if not all([p.exists() for p in rm_paths]):
		throw("checking parameters", f"Some of the videos to be removed do not exist.")

	if confirm_operation("Will remove the video below: ", rm_paths):
		# action
		for p in rm_paths:
			Path(p).unlink()
		rich.print("[bold green]Success![/bold green]")
		count_videos(config.curr_path)


@app.command()
def cut(
		clip_name: Annotated[str, typer.Argument(help="The video name to be cut.")],
		start_time: Annotated[
			str, typer.Argument(help="format: 01:02:03 for 1 hour 2 minutes 3 seconds.")],
		end_time: Annotated[str, typer.Argument(help="format: 01:02:03 for 1 hour 2 minutes 3 seconds.")],
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
	if confirm_operation(f"Will CUT the following video from [green]{start_time}[/green] to [green]{end_time}[/green]:",
						 [clip_input]):
		ffmpeg_cut(
			clip_input,
			start_time, end_time,
			clip_input.with_stem(clip_input.stem + "_output")
		)
		inplace(clip_input, is_backup)
		succeed_operation(config.curr_path)


@app.command()
def rename(
		clip_name: Annotated[str, typer.Argument(help="The video name to be renamed.")],
		new_name: Annotated[str, typer.Argument(help="The new name of the video.")],
):
	"""
	Rename a clip with a given new name(without suffix).
	If you need to rename the suffix, run `vmaker convert`.
	"""
	config = Config.load()
	clip_input = get_video_from_name(clip_name, config.curr_path)
	suffix = clip_input.suffix
	if confirm_operation(f"Will RENAME this following video to [green]{new_name}{suffix}[/green]:",
						 [clip_input]):
		clip_input.rename(clip_input.parent / (new_name + suffix))
		succeed_operation(config.curr_path)

@app.command()
def mute(
		clip_name: Annotated[str, typer.Argument(help="The video name to be operated.")],
		is_backup: Annotated[bool, typer.Option("--backup", "-b", help="Backup the original video or not.")] = True,
):
	"""
	Mute a video.
	"""
	config = Config.load()
	clip_input = get_video_from_name(clip_name, config.curr_path)
	if confirm_operation("Will MUTE the following video(s):", [clip_input]):
		ffmpeg_mute(
			clip_input,
			clip_input.with_stem(clip_input.stem + "_output")
		)
		inplace(clip_input, is_backup)
		succeed_operation(config.curr_path)


@app.command()
def speed(
		clip_name: Annotated[str, typer.Argument(help="The video name to be operated.")],
		speedx: Annotated[float, typer.Argument(help="The speed to be changed to, e.g. 0.5 means half speed, 2 means double speed.")],
		is_backup: Annotated[bool, typer.Option("--backup", "-b", help="Backup the original video or not.")] = True,
):
	"""
	Change the speed of a video.
	"""
	config = Config.load()
	clip_input = get_video_from_name(clip_name, config.curr_path)
	if confirm_operation(f"Will change the SPEED of the following video from 1.0x to {speedx}x, \nWhich means its duration will be changed from {to_hsm(ffprobe_duration(clip_input))} to about {to_hsm(int(ffprobe_duration(clip_input) / speedx))}:", [clip_input]):
		ffmpeg_speed(
			clip_input,
			clip_input.with_stem(clip_input.stem + "_output"),
			speedx
		)
		inplace(clip_input, is_backup)
		succeed_operation(config.curr_path)

@app.command()
def cfg():
	"""
	Show configs.
	"""
	config = Config.load()
	typer.echo(config)


@app.command()
def ls():
	"""
	list all videos in the current directory.
	"""
	config = Config.load()
	dir = config.curr_path
	all_files = list(dir.glob('**/*'))
	videos = [file for file in all_files if file.suffix in Lists.VIDEO_EXTS]
	rich.print(f"All videos in the current directory [green]{dir}[/green]:")
	print_videos_info(videos)
	rich.print(f"Total: [green]{len(videos)}[/green] videos.")
