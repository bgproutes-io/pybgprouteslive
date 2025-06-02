import websocket
import json
from _macros import WEBSOCKET_URL, MESSAGE_TYPE_ANNOUNCE, MESSAGE_TYPE_WITHDRAW
from _debug import Debug, DEBUG_ESSENTIAL, DEBUG_EXHAUSTIVE, DEBUG_NOTHING, DEBUG_TOO_MUCH


debugger = Debug(None)


class BGPLiveMsg:
    def __init__(self, msg):
        # General information about message
        self.isMessageOK = False
        self.record_type = None

        # BGP attributes
        self.prefixes    = list()
        self.aspath      = None
        self.communities = None
        self.nexthop     = None
        self.origin      = None

        # Timing information
        self.timestamp = None

        # Collector information
        self.vp_ip  = None
        self.vp_asn = None

        self._parse_bgp_msg(msg)

    
    def _parse_bgp_msg(self, msg):
        if "record_type" not in msg:
            debugger.wrn_msg("Unable to find the 'record_type' of message '{}'. Skiping this message.".format(msg), DEBUG_ESSENTIAL)
            return
        
        if msg["record_type"] == "update":
            self.record_type = MESSAGE_TYPE_ANNOUNCE
        elif msg["record_type"] == "withraw":
            self.record_type = MESSAGE_TYPE_WITHDRAW
        else:
            debugger.wrn_msg("Invalid record type '{}'. Skiping this message.".format(msg["record_type"]), DEBUG_ESSENTIAL)
            return
        
        if "vp" not in msg:
            debugger.wrn_msg("Unable to find the sending Vantage Point for message '{}'. Skiping this message.".format(msg))
        else:
            if "_" not in msg["vp"]:
                return
            
            self.vp_asn = int(msg["vp"].split("_")[0])
            self.vp_ip  = msg["vp"].split("_")[1]

        # Setting up the timestamp of the message 
        if "sec" in msg:
            self.timestamp = int(msg["sec"])

            if "Usec" in msg:
                self.timestamp += int(msg["Usec"]) / 1000000

        # Setting up all prefixes
        if "prefixes" in msg:
            for pfx in msg["prefixes"].split(","):
                self.prefixes.append(pfx)

        # Setting up the AS path
        if "as-path" in msg:
            self.aspath = msg["as-path"]

        # Setting up the BGP communities
        if "communities" in msg:
            self.communities = msg["communities"]

        # Setting up the nexthop
        if "nexthop" in msg:
            self.nexthop = msg["nexthop"]

        # Setting up the origin
        if "origin" in msg:
            self.origin = msg["origin"]

        self.isMessageOK = True



class BGProutesWebsocketClient:
    def __init__(self, APIkey):
        self.APIkey = APIkey

        self.url = "{}/?api_key={}".format(WEBSOCKET_URL, self.APIkey)

        self.websocket = websocket.create_connection(self.url)



    def _build_next_msg(self) -> BGPLiveMsg:
        try:
            raw_msg = self.websocket.recv()
        except websocket._exceptions.WebSocketConnectionClosedException:
            return None

        json_msg = json.loads(raw_msg)

        msg = BGPLiveMsg(json_msg)

        return msg
    

    
    def get_next_message(self):
        msg = self._build_next_msg()
        
        while not msg and msg.isMessageOK:
            msg = self._build_next_msg()

        return msg


if __name__ == "__main__":
    client = BGProutesWebsocketClient("6FYTaaSQbgSQ-eD2C5taVWEYCLIujEYGEV4BhCgphr8")

    while True:
        msg = client.get_next_message()

        print(msg.prefixes, msg.aspath)
