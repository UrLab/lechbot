import json
import logging
from copy import deepcopy
from fcntl import LOCK_EX, LOCK_UN, flock

logger = logging.getLogger()


class Persistent:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        try:
            self.fd = open(self.file, "r+")
        except:
            self.fd = open(self.file, "w+")
        flock(self.fd, LOCK_EX)
        try:
            self.db = json.load(self.fd)
            logger.debug("Loaded " + repr(self.db) + " from " + self.file)
        except:
            logger.exception("Cannot load from " + self.file)
            self.db = {}
        self._initial = deepcopy(self.db)
        return self.db

    def __exit__(self, *args, **kwargs):
        if self._initial != self.db:
            self.fd.seek(0)
            json.dump(self.db, self.fd)
            self.fd.truncate()
            logger.info("Saved " + repr(self.db) + " to " + self.file)
        flock(self.fd, LOCK_UN)
        self.fd.close()
