# Basic Concepts

## Recommended Workflow

Generally, Vmaker works in such a workflow: 

- Record videos with OBS or other recorders 

- Choose a satisfying video. Run `vmaker add`, adding it to the `clip_dir` folder.

- Run `vmaker cut`, `vmaker music`, `vmaker speed`, etc. to quickly modify the video without complicated GUI.

- Run `vmaker join` to quickly join clips to a video. You can add transitions to each clip.

## Nouns Explanation

### `cname`

`cname` is an argument existing in almost all commands. It is used to specify the name of the clip video to be operated. We have the following rules:

1. We will find the video according to your given `cname` in the folder `clip_dir`(configured when initiating).
2. You needn't give the suffix(such as `.mp4`) in `cname`, just the video name is available.
3. To simplify more, we can make a promise:
```shell
vmaker add 01-getting_started_with_python
```
Then the latest recorded video will be added to `clip_dir`, with a new name `01-getting_started_with_python.mp4`.

```shell
vmaker cut 01 00:00:00 00:01:12
```
`01`(the word before `-`) is considered as `01-getting_started_with_python.mp4`, which is our promise to simplify your command line.

### `rename_strategy`

`rename_strategy` is an option(`--rename` or `-r`) existing in almost all commands. In python code we have created a class for it like this:
```python
class RenameStrategies:
    NOT_GIVEN = 0
    DONT_RENAME = 1
    RENAME_WITH_TIME = 2
    RENAME_WITH_CLIP_INFO = 3
    RENAME_WITH_SUFFIX = 4
    # if giving a string instead an integer between 0 and 4, 
    # it means you manually give the new name instead of auto-generating one. 
```
For all the commands with the option `rename_strategy`, we have different default values.

For example, we expect not to rename the file when running `vmaker add`, and we expect to rename with a suffix, such as `_cut`/`_speed`/`_music` when running `vmaker cut/speed/music`.

It's very opinionated, but you can alter the default behaviour by:
- modifying the config file.
- giving an explicit `-r` option in your command.


## Advantages

### Compared with Adobe Premier Pro

You must have been tired of opening such a huge, bulky software after you finished long-time tutorial video recording. 

Are you using guns to fight against mosquitoes?

For example, you can use a single line `vmaker music bgm.mp3` to add a background music to your video. 10x operating/rendering speed faster than Adobe PR.

### Compared with just FFMpeg

FFMpeg offers an extremely rich set of features, to the extent that nearly all video editing software is based on it. The richness, however, brings complexity. Let’s take video concat as an example:

Using FFMpeg:
```text
(concat_list.txt)
file 'video1.mp4'
file 'video2.mp4'
file 'video3.mp4'
```

```shell
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.mp4
```

Using vmaker:

(Putting all videos to `clips` folder)
```shell
vmaker join output
```

Moreover, vmaker provides a full solution of managing your video clips. Learning from git and simply running `vmaker add`, you can manage your videos as the way of version control.


### Compared with online tools such as [video vinci](https://videovinci.com/)

When comes to online tools, you have to upload and download video files, which is a huge server load. The owner of these websites probably cannot afford to give everyone a free experience of using all the tools. Ads or payments have to be chosen as the only way.