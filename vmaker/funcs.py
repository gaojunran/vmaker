import os
from pathlib import Path
import shutil

from vmaker.utils import throw


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

def cut():
	pass