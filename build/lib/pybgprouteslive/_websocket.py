import websocket
import json
import requests
from ._macros import WEBSOCKET_URL, LIVE_MANAGER_URL, MESSAGE_TYPE_ANNOUNCE, MESSAGE_TYPE_WITHDRAW
from ._debug import Debug, DEBUG_ESSENTIAL, DEBUG_EXHAUSTIVE, DEBUG_NOTHING, DEBUG_TOO_MUCH
from ._exceptions import WebsocketConnectionError, PrefixToAPIKeyError
import time


CONNECTION_ERROR = 1
PARSING_ERROR = 2
MESSAGE_OK = 3


class BGPLiveMsg:
    def __init__(self, msg):
        # General information about message
        self.isMessageOK = False
        self.record_type = None

        # BGP attributes
        self.prefixes    = list()
        self.aspath      = ""
        self.communities = ""
        self.nexthop     = None
        self.origin      = None

        # Timing information
        self.timestamp = None

        # Collector information
        self.vp_ip  = None
        self.vp_asn = None

        self.err = None
        ok, err = self._parse_bgp_msg(msg)
        if not ok:
            self.err = err


    
    def _parse_bgp_msg(self, msg):
        if "record_type" not in msg:
            return False, "Unable to find the 'record_type' of message '{}'. Skiping this message.".format(msg)
        
        if msg["record_type"] == "update":
            self.record_type = MESSAGE_TYPE_ANNOUNCE
        elif msg["record_type"] == "withraw":
            self.record_type = MESSAGE_TYPE_WITHDRAW
        else:
            return False, "Invalid record type '{}'. Skiping this message.".format(msg["record_type"])
        
        if "vp" not in msg:
            return False, "Unable to find the sending Vantage Point for message '{}'. Skiping this message.".format(msg)
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

        return True, None
    

    def __str__(self):
        msg_type = "UNKOWN"

        if self.record_type == MESSAGE_TYPE_ANNOUNCE:
            msg_type = "U"
        
        if self.record_type == MESSAGE_TYPE_WITHDRAW:
            msg_type = "W"

        res = "{}|{}|{}|{}|{}|{}|{}|{}|{}".format(self.timestamp, msg_type, self.vp_asn, self.vp_ip, ",".join(self.prefixes), self.aspath, self.communities, self.origin, self.nexthop)

        return res



class BGProutesWebsocketClient:
    def __init__(self, APIkey):
        self.APIkey = APIkey
        self.prefixes = set()

        self.url = "{}/?api_key={}".format(WEBSOCKET_URL, self.APIkey)

        self.websocket = None

        self.debugger = Debug(None)



    def set_debug_level(self, level):
        self.debugger.set_debug_level(level)



    def set_debug_file(self, file):
        self.debugger.set_debug_file(file)



    def _build_next_msg(self) -> tuple[bool, BGPLiveMsg]:
        try:
            raw_msg = self.websocket.recv()
        except websocket._exceptions.WebSocketConnectionClosedException:
            return CONNECTION_ERROR, None

        try:
            json_msg = json.loads(raw_msg)
        except Exception:
            return PARSING_ERROR, raw_msg
        
        if "error" in json_msg:
            self.debugger.wrn_msg("Connection rejected: '{}'.".format(json_msg["error"]), DEBUG_ESSENTIAL)
            raise WebsocketConnectionError("Connection rejected: '{}'.".format(json_msg["error"]))

        msg = BGPLiveMsg(json_msg)
        if msg.err:
            self.debugger.wrn_msg(msg.err, DEBUG_EXHAUSTIVE)
            return PARSING_ERROR, msg

        return MESSAGE_OK, msg
    


    def _connect_websocket(self):
        self.websocket = websocket.create_connection(self.url)
    


    def subscribe_to_prefixes(self, prefixes :str):
        for pfx in prefixes.split(","):
            self.prefixes.add(pfx)

        url = "{}/update_live_prefixes?api_key={}&new_pfxs={}".format(LIVE_MANAGER_URL, self.APIkey, prefixes)

        response = requests.get(url)
        if response.status_code != 200:
            self.debugger.err_msg("Unable to setup the prefixes for the API. Receiving error '{}'.".format(response.content.decode()), DEBUG_ESSENTIAL)
            raise PrefixToAPIKeyError("Unable to setup the prefixes for the API. Receiving error '{}'.".format(response.content.decode()))
        
        self.debugger.debug("Prefixes successfully associated to your API key!", DEBUG_EXHAUSTIVE)
        return True
    

    
    def _get_next_message(self) -> BGPLiveMsg:
        ok, msg = self._build_next_msg()

        if ok == CONNECTION_ERROR:
            self.debugger.wrn_msg("Connection with websocket server has been shutdown.", DEBUG_ESSENTIAL)
            raise WebsocketConnectionError("Connection with websocket server has been cut off.")

        if ok == PARSING_ERROR:
            self.debugger.err_msg("Unable to parse message '{}' from the websocket server.".format(msg), DEBUG_ESSENTIAL)
        
        while ok != MESSAGE_OK or not msg.isMessageOK:
            ok, msg = self._build_next_msg()

        return msg
    


    def get_messages(self):
        if self.websocket is None:
            self._connect_websocket()
            
        while True:
            try:
                msg = self._get_next_message()
                yield msg

            except KeyboardInterrupt:
                self.debugger.debug("Receiving ^C signal, client exits. The association between your API kay and the requested prefixes will be removed after 4 hours of inactivity from your API key. In case it has been removed, you can recreate it using the 'subscribe_to_prefixes' method of this class.", DEBUG_EXHAUSTIVE)
                return



REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"


if __name__ == "__main__":
    client = BGProutesWebsocketClient("6FYTaaSQbgSQ-eD2C5taVWEYCLIujEYGEV4BhCgphr8")

    client.subscribe_to_prefixes(REQUIRED_PREFIX)
    time.sleep(1)

    for msg in client.get_messages():
        txt = "{}|{}|{}_{}|{}|{}".format(int(msg.timestamp), ",".join(sorted(msg.prefixes)), msg.vp_asn, msg.vp_ip, msg.aspath, msg.communities)
        print(txt)
