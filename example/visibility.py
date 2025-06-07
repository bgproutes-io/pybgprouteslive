from pybgprouteslive import BGProutesWebsocketClient, MESSAGE_TYPE_ANNOUNCE, MESSAGE_TYPE_WITHDRAW
import os

REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"

if __name__ == "__main__":
    ribs = dict()   # This RIB can be initialized using our wonderful historical data API !

    client = BGProutesWebsocketClient(os.environ["BGP_API_KEY"])
    client.subscribe_to_prefixes(REQUIRED_PREFIX)

    for msg in client.get_messages():
        if msg.record_type == MESSAGE_TYPE_ANNOUNCE:
            vp = (msg.vp_asn, msg.vp_ip)

            if vp not in ribs:
                ribs[vp] = set()

            for prefix in msg.prefixes:     # Iterate over all prefixes
                ribs[vp].add(prefix)

        if msg.record_type == MESSAGE_TYPE_WITHDRAW:
            for prefix in msg.prefixes:     # Iterate over all prefixes
                if prefix in ribs[vp]:
                    print("We lost visibility on prefix '{}' on Vantage Point '{}'.".format(prefix, vp))

                    ribs[vp].remove(prefix)