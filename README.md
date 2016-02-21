# LechBot
**IRC integration of UrLab**

## Installation

    $ git clone git@github.com:urlab/lechbot
    $ cd lechbot
    $ virtualenv -p python3.4 ve3
    $ source ve3/bin/activate
    $ pip install -r requirements.txt

## Configuration && run

Create a file called local_config.py (in the same directory as config.py), and edit config values as needed.
In order to test the bot locally, you might be interested in runnning an instance of [UrLab's Incubator](https://github.com/UrLab/incubator) and a 
[crossbar](http://crossbar.io) broker.

### Test in command line only

`$ python lechbot.py [ --debug ]`

### Connect to irc

`$ python lechbot.py --irc [ --debug ]`
