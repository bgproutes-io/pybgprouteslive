from pybgprouteslive import BGProutesWebsocketClient


REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"


if __name__ == "__main__":
    client = BGProutesWebsocketClient("6FYTaaSQbgSQ-eD2C5taVWEYCLIujEYGEV4BhCgphr8")

    client.subscribe_to_prefixes(REQUIRED_PREFIX)

    for msg in client.get_messages():
        txt = "{}|{}|{}_{}|{}|{}".format(int(msg.timestamp), ",".join(sorted(msg.prefixes)), msg.vp_asn, msg.vp_ip, msg.aspath, msg.communities)
        print(txt)