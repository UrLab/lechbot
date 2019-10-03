import asyncio
from ircbot.plugin import BotPlugin
import paho.mqtt.client as mqtt
import json
from datetime import datetime

class MQTTPlugin(BotPlugin):
    """
    MQTT subscriber for lechbot.
    """

    def __init__(self, host, topics, ratelimit):
        self.host = host
        self.topics = topics
        self.last_seen_keys = {}
        self.ratelimit = ratelimit

        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = self.on_mqtt_connect
        self.mqtt.on_message = self.on_mqtt_message

    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.bot.log.info("Connected to MQTT")
        for topic in self.topics:
            self.mqtt.subscribe(topic)

    def on_mqtt_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        try:
            data = json.loads(payload)
        except Exception as e:
            self.bot.log.info("Got incorrect message: " + str(payload) + " (%s)" % e)
            return

        key = data.get("key")
        text = data.get("text")
        now = datetime.now()

        if not (key and text):
            self.bot.log.info("Missing informations in the message: " + repr(data))
            return

        # Rate limit
        last_seen = self.last_seen_keys.get(key, datetime.fromtimestamp(0))
        if (now - last_seen).total_seconds() < self.ratelimit.get(key, 0):
            self.bot.log.info("Got rate-limited event " + repr({
                'key': key, 'time': now, 'text': text
            }) + " / Last seen: " + repr(last_seen))
            return

        self.say(text)
        self.bot.log.debug("Got " + repr({
            'key': key, 'text': text
        }))

        self.last_seen_keys[key] = now


    @asyncio.coroutine
    def loop(self):
        self.mqtt.loop()

    @BotPlugin.on_connect
    def startup(self):
        self.bot.log.debug("Starting.")
        self.mqtt.connect(self.host)
        while True:
            yield from self.loop()
