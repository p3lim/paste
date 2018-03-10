# paste

A (very) basic pastebin application written in Python.

Features:
- File/form upload
- Syntax highlighted and raw views
- Support for images
- Link to and highlight specific lines
- Intentionally designed [for Docker](https://github.com/p3lim/docker-paste)

Planned:
- Multithread
- Render markdown
- URL shortening

## How to run

- Build with docker (or use the [official one](https://hub.docker.com/r/p3lim/paste/))
- Run with docker
- Paste away

## Plugins

- [Sublime Text 3](https://github.com/p3lim/sublime-paste)
- Bash:
  ```
  paste(){
    link=$(curl -sF "c=@${1:--}" http://example.com)
    notify-send "$link"
    xclip -selection clipboard <<< "$link"
  }
  ```
