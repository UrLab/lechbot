import json
from fcntl import flock, LOCK_UN, LOCK_EX
import logging

logger = logging.getLogger()


class Persistent:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        try:
            self.fd = open(self.file, 'r+')
        except:
            self.fd = open(self.file, 'w+')
        flock(self.fd, LOCK_EX)
        try:
            self.db = json.load(self.fd)
            logger.debug("Loaded " + repr(self.db) + " from " + self.file)
        except:
            logger.exception("Cannot load from " + self.file)
            self.db = {}
        return self.db

    def __exit__(self, *args, **kwargs):
        self.fd.seek(0)
        json.dump(self.db, self.fd)
        self.fd.truncate()
        flock(self.fd, LOCK_UN)
        self.fd.close()
        logger.info("Saved " + repr(self.db) + " to " + self.file)
