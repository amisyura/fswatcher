#FSWatcher

Watching a folder and run received command if one of the files will be changed.

##Install
```shell
pip install -r requirements.txt
```

##Usage

```shell
fswatcher.py -c CMD [CMD ...] [-d [DELAY]] [-f] [-v] [-h] path
```

######Required arguments:
* **-c CMD [CMD ...], --cmd CMD [CMD ...]** - One or more shell commands for execute
* **path** - the path that you want to watching (is required)

######Optional arguments:
* **-d [DELAY], --delay [DELAY]** - delay in seconds after which the command will be executed
* **-f, --files** - show changed files snapshot
* **-v, --verbose** - increase verbosity

####Example
```shell
fswatcher.py ~/dev/mysite/ -d=2 -c="rsync -az --delete --exclude=.git /Users/username/dev/mysite dev@dev.host.com/dev/mynewsite"
```
####or
```shell
fswatcher.py ~ -d=10 -c="ls -la ~ > snapshot.log"
```