import math
import os
import shutil
import subprocess
from pathlib import Path

import ffmpeg

from vmaker.utils import throw, is_valid_path




def _check_config_valid(**kwargs):
	is_valid = is_valid_path(kwargs.get("raw_dir"), allow_not_exist=True) and is_valid_path(kwargs.get("clip_dir"),
																							allow_not_exist=True) and is_valid_path(
		kwargs.get("output_dir"), allow_not_exist=True)
	is_valid or throw("...", "Incorrect CONFIG. Run `vmaker init` again.")


def copy(source: Path, dest: Path):
	"""
	Copy files from a dir to another. Two arguments are `Path` type of files.
	"""
	if os.path.exists(dest):
		throw("copying", f"The file already exists in {dest}!")
		return False
	try:
		shutil.copy2(source, dest)
	except Exception as e:
		throw("copying", str(e))
		return False


def ffmpeg_cut(clip_input: Path, start_time: str, end_time: str, clip_output: Path):
	ffmpeg.input(str(clip_input.resolve())) \
		.filter('trim', start=start_time, end=end_time) \
		.output(str(clip_output.resolve())) \
		.run()


def ffmpeg_mute(clip_input: Path, clip_output: Path):
	video_input = ffmpeg.input(str(clip_input.resolve()))
	audio = video_input.audio.filter('volume', 0)
	ffmpeg.output(audio, video_input.video, str(clip_output.resolve())) \
		.run()

def ffmpeg_convert(clip_input: Path, clip_output: Path):
	ffmpeg.input(str(clip_input.resolve())) \
		.output(str(clip_output.resolve())) \
		.run()

def ffmpeg_speed(clip_input: Path, clip_output: Path, speed: float):
	video_input = ffmpeg.input(str(clip_input.resolve()))
	video = video_input.video.filter('setpts', f'{1 / speed}*PTS')
	audio = video_input.audio.filter('atempo', speed)
	ffmpeg.output(video, audio, str(clip_output.resolve())) \
		.run()


def ffprobe_duration(clip_input: Path):
	seconds = math.floor(float(str(subprocess.run(f"ffprobe -i {clip_input} -show_entries format=duration -v quiet -of csv=\"p=0\"", stdout=subprocess.PIPE).stdout, encoding="utf-8").strip()))
	return seconds
