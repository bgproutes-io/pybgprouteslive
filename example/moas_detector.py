from pybgprouteslive import BGProutesWebsocketClient, MESSAGE_TYPE_ANNOUNCE
import os

REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"
ribs = dict()   # This RIB can be initialized using our wonderful historical data API !

client = BGProutesWebsocketClient(os.environ["BGP_API_KEY"])
client.subscribe_to_prefixes(REQUIRED_PREFIX)

for msg in client.get_messages():
    if msg.record_type != MESSAGE_TYPE_ANNOUNCE:
        continue

    vp = (msg.vp_asn, msg.vp_ip)
    origin_as = msg.aspath.split()[-1]

    for prefix in msg.prefixes:
        if ribs.get(vp, {}).get(prefix) != origin_as:
            print(f"Origin change detected! {prefix}: {ribs.get(vp, {}).get(prefix)} -> {origin_as}")
        ribs.setdefault(vp, {})[prefix] = origin_as
        