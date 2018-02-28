# paste

A (very) basic pastebin application written in Python.

Features:
- File/form upload
- Syntax highlighted and raw views
- Link to and highlight specific lines
- Intentionally designed for Docker

Planned:
- Multithread
- Render markdown
- Render images
- URL shortening

## How to run

- Clone this repo
- Build with docker
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
