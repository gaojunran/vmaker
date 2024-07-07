class RenameStrategies:
	NOT_GIVEN = 0
	DONT_RENAME = 1
	RENAME_WITH_TIME = 2
	RENAME_WITH_CLIP_INFO = 3
	RENAME_WITH_SUFFIX = 4


class Lists:
	CONFIG_LIST = ["raw_dir", "clip_dir", "output_dir"]
	DIR_CONFIG_LIST = ["raw_dir", "clip_dir", "output_dir"]
	VIDEO_EXTS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]