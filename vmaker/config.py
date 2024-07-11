import json
import os
import platform
import subprocess
from copy import copy
from pathlib import Path
from vmaker.constants import Lists, Dicts


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

class Config:

	def __init__(self, raw_dir, clip_dir, output_dir, curr_dirname):
		self.raw_path = Path(raw_dir)
		self.clip_path = Path(clip_dir)
		self.output_path = Path(output_dir)
		self.curr_path = Path(self.clip_path / curr_dirname)
		self.curr_path.mkdir(parents=True, exist_ok=True)


	# factory method
	@classmethod
	def load(cls) -> "Config":
		from vmaker.utils import throw
		config_json = json.loads(os.getenv("VMAKER_CONFIG"))

		if not all(config_json.get(key) for key in Lists.CONFIG_LIST):
			throw("initializing", "Config missing. Please run `vmaker init`.")

		config = Config(config_json.get("raw_dir"), config_json.get("clip_dir"), config_json.get("output_dir"), config_json.get("curr_dirname"))
		return config


	@classmethod
	def dump(cls, config: "Config"):
		config_dict = copy(Dicts.CONFIG_TEMPLATE)
		config_dict["raw_dir"] = str(config.raw_path)
		config_dict["clip_dir"] = str(config.clip_path)
		config_dict["output_dir"] = str(config.output_path)
		_set_env_var("VMAKER_CONFIG", json.dumps(config_dict))


if __name__ == '__main__':
