import json
import os
import platform
import subprocess
from pathlib import Path
import shutil

import ffmpeg

from vmaker.utils import throw


def _is_valid_path(s):
	try:
		return Path(s).exists()
	except OSError:
		return False


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


def _check_config_valid(**kwargs):
	is_valid = _is_valid_path(kwargs.get("raw_dir")) and _is_valid_path(kwargs.get("clip_dir")) and _is_valid_path(
		kwargs.get("output_dir"))
	is_valid or throw("...", "Incorrect CONFIG. Run `vmaker init` again.")


def env_update(**kwargs):
	_check_config_valid(**kwargs)
	_set_env_var("VMAKER_CONFIG", json.dumps(kwargs))


def copy(source: Path, dest: Path):
	"""
	Copy files from a dir to another. Two arguments are all `Path` of files.
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
