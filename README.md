# LechBot
**IRC integration of UrLab**


## Installation via docker

```bash
# build l'image
podman build -t lechebot .
# pour usage rapide:
# --rm le docker est supr au moment de le stop
podman run --rm --volume ./data:/lechebot/data lechebot
podman run -it --rm --volume ./data:/lechebot/data lechebot bash # run bash to manually start lechbot and choose comand line options
```

## data

the data/ folder is shared with the container

## Installation en local
```bash
$ git clone git@github.com:urlab/lechbot
$ cd lechbot
$ virtualenv -p python3.9 ve3
$ source ve3/bin/activate
$ pip install -r requirements.txt
```

## Configuration & run

Create a file called local_config.py (in the same directory as config.py), and edit config values as needed.
In order to test the bot locally, you might be interested in runnning an instance of [UrLab's Incubator](https://github.com/UrLab/incubator).

to use the `sudo` plugin you need to add a sudoers.json files in the data/ dir

sudoers.json:
```json
{
    "users": []
}
```
with the user names of the sudoers in the users array (you can allways add some later using the bot command or by modifying the file)

### Test in command line only

`$ python lechbot.py [ --debug ]`

For a minimal setup, add `--local` so that lechbot won't try to poll from twitter or other distant APIs.

### Connect to irc

`$ python lechbot.py --irc [ --debug ]`

### Write your own bot

See the documentation's [quickstart](doc/source/index.rst)
