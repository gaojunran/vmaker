# Vmaker - Tutorial video maker for programmers

## Dependency
Our project is based on [Typer](https://typer.tiangolo.com/), [FFMpeg](https://ffmpeg.org/) and [ffmpeg-python](https://github.com/kkroening/ffmpeg-python).


## 已实现/规划中的功能
非ffmpeg
1. init
2. curr
3. add
4. rm
5. cfg
6. 


ffmpeg
- cut
- join *
- music *
- mute *
- speed *
- volume *
- bar *
- subtitle ()
- 扩展功能 导入moviepy代码 eval函数来执行
- 扩展功能 导入ffmpeg命令 eval函数来执行

## 重命名策略

所有ffmpeg操作函数（除了join）的默认命名策略：
原文件名 + 原文件后缀 + .output

然后可以使用指定的命名策略进行二次修改。

add/remove默认需要名字；

## 备份策略

所有需要用户指定是否备份的命令，默认都是备份。还没想好这块的具体逻辑。







