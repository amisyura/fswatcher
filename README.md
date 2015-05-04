#FSWatcher

Watching a folder and run received command if one of the files will be changed.

###Install
```shell
pip install -r requirements.txt
```

###How to use

```shell
fswatcher.py [-h] -c [CMD] [-d [DELAY]] [-v] path
```

* **path** - the path that you want to watching (is required)
* **-c** - the shell command for execute
* **-d** - delay in seconds after which the command will be executed
* **-v** - verbose output

#####Example
```shell
fswatcher.py ~/dev/mysite/ -d=2 -c="rsync -az --delete --exclude=.git /Users/username/dev/mysite dev@dev.host.com/dev/mynewsite"
```
##### or
```shell
fswatcher.py ~ -d=10 -c="ls -la ~ > snapshot.log"
```