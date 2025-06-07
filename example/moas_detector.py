from pybgprouteslive import BGProutesWebsocketClient, MESSAGE_TYPE_ANNOUNCE
import os

REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"

if __name__ == "__main__":
    ribs = dict()   # This RIB can be initialized using our wonderful historical data API !

    client = BGProutesWebsocketClient(os.environ["BGP_API_KEY"])
    client.subscribe_to_prefixes(REQUIRED_PREFIX)

    for msg in client.get_messages():
        if msg.record_type != MESSAGE_TYPE_ANNOUNCE:    # Ignore non update messages
            continue

        vp = (msg.vp_asn, msg.vp_ip)
        origin_as = msg.aspath.split(" ")[-1]

        if vp not in ribs:
            ribs[vp] = dict()

        for prefix in msg.prefixes:     # Iterate over all prefixes
            if prefix not in ribs[vp]:
                ribs[vp][prefix] = origin_as

            if origin_as != ribs[vp][prefix]:
                print("Origin change detected! Old origin was '{}' and new origin i '{}'.".format(ribs[vp][prefix], origin_as))

            ribs[vp][prefix] = origin_as
