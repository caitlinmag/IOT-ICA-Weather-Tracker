from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.models.consumer.v3.channel import Channel

from config import config

pn_config = PNConfiguration()
pn_config.subscribe_key = config.get("PUBNUB_SUBSCRIBE_KEY")
pn_config.publish_key = config.get("PUBNUB_PUBLISH_KEY")
pn_config.secret_key = config.get("PUBNUB_SECRET_KEY")
pn_config.uuid = config.get("PUBNUB_USER_ID")
pubnub = PubNub(pn_config)
