import json
import os
from pathlib import Path

from vmaker.constants import Lists



def check_config_exists(config: dict):
	return all(config.get(key) for key in Lists.CONFIG_LIST)


class Config:

	def __init__(self, raw_dir, clip_dir, output_dir, curr_dirname):
		self.raw_path = Path(raw_dir)
		self.clip_path = Path(clip_dir)
		self.output_path = Path(output_dir)
		self.curr_path = Path(self.clip_path / curr_dirname)


	# factory method
	@classmethod
	def load(cls):
		from vmaker.utils import throw
		config_json = json.loads(os.getenv("VMAKER_CONFIG"))
		check_config_exists(config_json) or throw("initializing", "Config missing. Please run `vmaker init`.")
		config = Config(config_json.get("raw_dir"), config_json.get("clip_dir"), config_json.get("output_dir"), config_json.get("curr_dirname"))
		return config



	@classmethod
	def dump(cls):
		pass



if __name__ == '__main__':




