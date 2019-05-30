# Python IMAP Dumper

A Python script to download your IMAP emails to .eml files and, optionally, delete it from server.

## Install

```console
$ git clone https://github.com/marttosc/imap-dumper
$ cd imap-dumper
$ pip install -r requirements.txt
```
## Usage

```console
$ python dump_imap.py -s SERVER [-p PORT] -u USERNAME [-P PASSWORD] [-r REMOTE_FOLDER] [--list] [-l LOCAL_FOLDER] [-d DELETE_REMOTE] [-t TRASH_FOLDER]
```

| Argument | Description | Default Value | Required |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|:-------------:|:--------:|
| `-s`, `--server` | IMAP server, like imap.gmail.com |  | **Yes** |
| `-p`, `--port` | IMAP port | `993` | No |
| `-u`, `--username` | IMAP username |  | **Yes** |
| `-P`, `--password` | IMAP password. If not informed, will be prompted. |  | Yes |
| `-r`, `--remote-folder` | Remote folder(s) to download, could be take more than one folder separating them with comma. If not informed, all the folders will be downloaded. | `*` | No |
| `-l`, `--local-folder` | Absolute path of local folder where the .eml files should be saved. | `.` | No |
| `--list` | List the remote folders name and exit. |  | No |
| `-d`, `--delete-remote` | If informed, the messages will be moved to the remote trash folder and flagged as deleted. |  | No |
| `-t`, `--trash-folder` | Remote trash folder name | `Trash` | No |

## Examples

```console
$ python dump_imap.py -s imap.gmail.com -u your-email@gmail.com --list
$ python dump_imap.py -s imap.gmail.com -u your-email@gmail.com -r inbox -l /home/user/imap
$ python dump_imap.py -s imap.gmail.com -u your-email@gmail.com -r inbox,inbox.documents -l /home/user/imap -d -t
```

