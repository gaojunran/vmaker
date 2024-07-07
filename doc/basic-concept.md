# Basic Concept

## Workflow

Generally, Vmaker works in such a workflow: 

- Record videos with OBS or other recorders 

- Choose a satisfying video. Run `vmaker add`, adding it to the `clips` folder.

- Run `vmaker cut`, `vmaker music`, `vmaker speed`, etc. to quickly modify the video without complicated GUI.

- Run `vmaker join` to quickly join clips to a video. You can add transitions to each clip.


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