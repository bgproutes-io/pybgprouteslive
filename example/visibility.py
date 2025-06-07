from pybgprouteslive import BGProutesWebsocketClient, MESSAGE_TYPE_ANNOUNCE, MESSAGE_TYPE_WITHDRAW
import os

REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"
ribs = dict()   # This RIB can be initialized using our wonderful historical data API !

client = BGProutesWebsocketClient(os.environ["BGP_API_KEY"])
client.subscribe_to_prefixes(REQUIRED_PREFIX)

for msg in client.get_messages():
    vp = (msg.vp_asn, msg.vp_ip)

    if msg.record_type == MESSAGE_TYPE_ANNOUNCE:
        ribs.setdefault(vp, set()).update(msg.prefixes)

    elif msg.record_type == MESSAGE_TYPE_WITHDRAW:
        for prefix in msg.prefixes:
            if prefix in ribs.get(vp, set()):
                print(f"Visibility lost for {prefix} at {vp}")
                ribs[vp].remove(prefix)