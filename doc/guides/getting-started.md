# Getting started

::: warning
Vmaker is still actively developing, so all the release versions are for trial. Some of the features may be unstable. You can post an issue [here](https://github.com/gaojunran/vmaker/issues).
:::

## Quick install

### From PyPI (recommended)

Vmaker has been published to pypi, which means you can easily get it with your favourite python package manager.

::: code-group
```shell [pipx]
# You need to have `pipx` in your PATH first.
pipx install vmaker
```

```shell [pip]
pip install --user vmaker
```
:::

Moreover, install **FFMpeg** and add it to `PATH` environment variable to make sure vmaker works correctly.

### From a software/package manager

We have supported **scoop**(for Windows) and **homebrew**(for Mac/Linux). 

Installing vmaker in this way will automatically detect and install FFMpeg.

::: code-group
```shell [scoop]

scoop install vmaker
```

```shell [brew]

brew install vmaker
```
:::

### Executable version

We have also provided executable versions for those who are not familiar with python and focus on video editing. However, these versions might have a slower rhythm of releasing. 


## The simplest way of using Vmaker

Initiate Vmaker, giving the necessary config to vmaker to make sure it works correctly:

```shell
vmaker init
```

Then a `default` folder will be added to `clip_dir`. You can specify another name(for example `tutorial`):

```shell
vmaker curr tutorial
```

Once you finished the recording of a video, run one of the following commands:

::: code-group
```shell [simplest]
vmaker add
# It will add the **latest**(based on the modified time) video.

```

```shell [with a new name]
vmaker add 01-getting-started
# It will add the **latest**(based on the modified time) video
# with a new name `01-getting-started`(the suffix is automatically added).
```


```shell [choose one]
vmaker add -c
# It will invoke a prompt to ask you to choose one video from a list.
```

:::
Then a video will be copied from `raw_dir`(the path where videos are recorded) to `current_dir`(the path where clips are saved now).

Once you add a video with the command `vmaker add [...]`, you can easily modify a video: 
```shell
# record one video, then:
vmaker add 01-getting-started
# record another video, then:
vmaker add 02-quick-install
# choose a video by its shortest name and modify it
vmaker music 01 bgm.mp3
vmaker cut 02 ~ 00:20:00 # (`~` means the argument is omitted)
```

::: info
Different commands have different renaming strategies. See 
:::

If every clip has been modified, you can run one of the following commands to concatenate all the videos:
::: code-group
```shell [simplest]
vmaker join
# The output video has the same name as `current_dir`.
```

```shell [with a new name]
vmaker join tutorial_final.mkv
# Explicitly specify the output name with a suffix.
```
:::

