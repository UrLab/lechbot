# LechBot
**IRC integration of UrLab**

## Installation

    git clone git@github.com:titouanc/lechbot
    cd lechbot
    virtualenv -p python3.4 ve3
    source ve3/bin/activate
    pip install -r requirements.txt

## Configuration && run

Create a file called local_config.py (in the same directory as config.py), and edit config values as needed.
In order to test the bot locally, you might be interested in runnning an instance of [UrLab's Incubator](https://github.com/UrLab/incubator).

Then `python lechbot.py`. By default, it will run in an interactive shell without connecting to IRC. To connect to IRC, set the config value `BOT_HAL = IRCBot`.
