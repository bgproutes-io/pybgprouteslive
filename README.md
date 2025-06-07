# BGProutes live data documentation

Welcome to the BGProutes.io websocket, an efficient gateway to get real-time information about your BGP ressources. The websocket server is running at address 'wss://websocket.bgproutes.io', on port 443. It offers the ability to any authentified user to get real-time data streams of BGP data corresponding to a set of required prefixes.

The pipeline is using Kafka to gather data for the requested prefixes from all our BGP collectors. The user can them identify using its API key and the websocket server then connects to the right kafka topic to get all the corresponding data. 

Note that, while this project is working in practice, we are still in development phase, and the service can experience short unavailabilities or bug.

## Websocket documentation

As mentioned earlier, the websocket is accessible at 'wss://websocket.bgproutes.io', on port 443. We will detail the process that a user must follow to be able to get the real-time stream of data. Do not be scared, this process might be way faster than reading this documentation!

In addition, if you want to speed up the process even more, we invite you to use our [python client](https://github.com/bgproutes-io/pybgprouteslive/).

### Authentication

The websocket works on an "API-key -> prefixes" association. You need to connect on the website and go to the "API key page". To get started, first generate an API key and fill the list of associated prefixes. This must be a single list of prefixes, comma separated, e.g., "192.23.62.0/24,2a06:3040:10::/48". This will start the association of your API key with the list of prefixes you want to get the data for. Note that you can also provide an empty list of prefixes in case you just want to create the API key.

When the API key is created, please make sure to write it in a secure place, your API key is not stored in our database, so there is no way to get it if you forget it.

Also note that if your API key is associated to one or more prefixes and you did not use is for 4 hours, the association will be discarded (but the API key will still remain, only the list of prefixes will be replaced by an empty list). We added this threshold as unused API keys may consume some ressources on our infrastructure.

In case you do not want to use the website to associate your API key to a set of prefixes or update this set of prefixes, you can use our live manager api, running at https://live-manager-api.bgproutes.io/ (port 443). You can use the "/update_live_prefixes" endpoint to setup or update the association. Your API must be created to be able to use this API. 

example: "curl https://live-manager-api.bgproutes.io/update_live_prefixes?api_key=YOUR_API_KEY&new_pfxs=YOUR_LIST_OF_PREFIXES_COMMA_SEPARATED"

Note that this process can be done easily with one line of code using our [python client](https://github.com/bgproutes-io/pybgprouteslive/).

Then you can just get the data about your requests prefixes by connecting to the websocket using the following address:
wss://websocket.bgproutes.io/?api_key=YOUR_API_KEY


### Rate limiting

Each API key is subject to usage limits to ensure fair access for all users. You can only setup a redirection toward 10 prefixes at maximum.
If you need more prefixes, please send an email to contact@bgproutes.io, we will be happy to help you and discuss about your use-case !

## Python client documentation

To help users to easily get data from BGProutes.io, we developed [pybgprouteslive](https://github.com/bgproutes-io/pybgprouteslive/), a python package designed to associate an API key to a set of prefixes, update this association, and get the data from the websocket server.

### Installation

To start with the installation, clone the git repo of the python package.

```bash
git clone https://github.com/bgproutes-io/pybgprouteslive.git
```

Then simply install the package locally with:

```bash
python3 -m pip install .
```

Note that the package requires both "websocket-client" and "requests" installed. Additionally, if you have package "websockets" installed, it might conflict with package "websocket-client". In this case consider using a virtual environment, if not already the case.

### pybgprouteslive package

The [pybgprouteslive](https://github.com/bgproutes-io/pybgprouteslive/) provides two main classes that enable to process BGP data, "BGPLiveMsg" and "BGProutesWebsocketClient".

The main object is BGProutesWebsocketClient wich contains all the methods required to get real-time data from BGProutes.io. This object must be created with one argument, which is your API key:

```python
client = BGProutesWebsocketClient(YOUR_API_KEY)
```

or, more secured:

```bash
export BGP_API_KEY=your-api-key
```

and 

```python3
import os

your_api_key = os.environ["BGP_API_KEY]
client = BGProutesWebsocketClient(your_api_key)
```

This new "client" object has two main methods. First "subscribe_to_prefixes(pfx_list :str)" that enables to subscribe to a list of prefixes with your API key. Second, the method "get_messages" which yields objects "BGPLiveMsg", until it receives ^C. Here is a full example:

```python3
import os

your_api_key = os.environ["BGP_API_KEY]
REQUIRED_PREFIXES = "192.23.62.0/24,2a06:3040:10::/48"

client = BGProutesWebsocketClient(your_api_key)
client.subscribe_to_prefixes(REQUIRED_PREFIXES)

for msg in client.get_messages():
    print(msg)
```

In case the client is not able to connect to the websocket server (e.g., if the API key is invalid, if another client is already connected with the same API key, ...), the client will raise an "WebsocketConnectionError". In case the association between the API key and the list of prefixes fails, the client will raise an "PrefixToAPIKeyError".


The "BGPLiveMsg" class represents a BGP message received by the websocket client, and contains the following fields:

```python
class BGPLiveMsg:
    def __init__(self, msg):
        self.isMessageOK = False
        self.record_type = None
        self.prefixes    = list()
        self.aspath      = ""
        self.communities = ""
        self.nexthop     = None
        self.origin      = None

        self.timestamp = None

        self.vp_ip  = None
        self.vp_asn = None
```

This class can be printed using "str(msg)", and appears as follow:

```python
res = "{}|{}|{}|{}|{}|{}|{}|{}|{}".format(self.timestamp, msg_type, self.vp_asn, self.vp_ip, ",".join(self.prefixes), self.aspath, self.communities, self.origin, self.nexthop)
```

"msg_type" is "U" in case of an update message, "W" in case of a withdraw, and "UNKNOWN" otherwise.


### Examples

Here is an example of a simple AS origin change to monitor your prefixes:

```python3
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
```

Here is an example of a simple prefix visibility analyzer.

```python3
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
```

### Licence

GPLv3

_____________________________________

For bug reports or feedback, feel free to reach out at contact@bgproutes.io.

Enjoy querying BGP data! 🌐
