import yaml
import plugins
from functools import partial


def plugin_factory(plugin_name, args):
    """
    Return a callable with no arguments to instantiante a plugin
    """
    py_class = getattr(plugins, plugin_name)
    if isinstance(args, dict):
        return partial(py_class, **args)
    elif isinstance(args, list):
        return partial(py_class, *args)
    elif args is not None:
        return partial(py_class, args)
    else:
        return py_class


def load_config(filename):
    config_file = yaml.load(open(filename))
    groups = {
        name: [plugin_factory(*x) for x in fragment.items()]
        for name, fragment in config_file['groups'].items()
    }

    chans = {}
    for chan, config in config_file['chans'].items():
        chan_plugins = [
            plugin_factory(*x)
            for x in config.get('plugins', {}).items()
        ]
        for group in config.get('groups', []):
            chan_plugins += groups[group]
        yield chan, chan_plugins



if __name__ == "__main__":
    from sys import argv

    config_filename = argv[1] if len(argv) > 1 else "exampleconfig.yml"
    for chan, chan_plugins in load_config(config_filename):
        print(chan)
        print([plugin() for plugin in chan_plugins])
        print()
