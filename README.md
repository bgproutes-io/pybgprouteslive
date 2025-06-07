# 📡 bgproutes.io real-time data access

Welcome to **bgproutes.io**’s real-time stream — your gateway to live BGP data. This service offers authenticated users low-latency access to BGP updates collected from the vantage points listed on our [vantage_points](/vantage_points) page.
These updates are sourced from platforms that support real-time streaming: `bgproutes.io`, `ris`, and `routeviews`.
For `pch` and `cgtf`, real-time data is not available, but you can still access their historical records through the bgproutes.io API [bgproutes.io API](https://bgproutes.io/data_api/).

We stream data in real time through our WebSocket server, available at:

```bash
wss://websocket.bgproutes.io
```

The server runs over port 443 and delivers live BGP updates for the IP prefixes configured by each client (and associated to an API key).
Our backend uses Apache Kafka to manage and deliver BGP updates. When a user connects via WebSocket using their API key, the server subscribes to the appropriate Kafka topics to stream updates for the selected prefixes.
We exlain in this [page](https://bgproutes.io/data_realtime/) how to directly access our WebSocket (without our Python client).

Below, we explain how to use our Python client, which is highly recommend as it simplifies authentication, connection handling, and data parsing.

---

## 📦 Installation

```bash
git clone https://github.com/bgproutes-io/pybgprouteslive.git
cd pybgprouteslive
python3 -m pip install .
```

> Dependencies: `websocket-client` and `requests`. Avoid conflicts with `websockets` by using a virtual environment.

---

## 🧠 Main Components

#### `BGProutesWebsocketClient`

This is your main interface to the WebSocket server:

```python
from pybgprouteslive import BGProutesWebsocketClient
client = BGProutesWebsocketClient("YOUR_API_KEY")
```

To securely use environment variables:

```bash
export BGP_API_KEY=your-api-key
```

```python
import os
client = BGProutesWebsocketClient(os.environ["BGP_API_KEY"])
```

#### Methods

* `subscribe_to_prefixes(prefixes: str)` — Subscribe to a comma-separated list of prefixes.
* `get_messages()` — Yield incoming `BGPLiveMsg` objects indefinitely (until interrupted).

Example:

```python
REQUIRED_PREFIXES = "192.23.62.0/24,2a06:3040:10::/48"
client.subscribe_to_prefixes(REQUIRED_PREFIXES)

for msg in client.get_messages():
    print(msg)
```

#### 📬 `BGPLiveMsg` Object

Represents a BGP message with fields like:

```python
class BGPLiveMsg:
    self.isMessageOK
    self.record_type
    self.prefixes
    self.aspath
    self.communities
    self.nexthop
    self.origin
    self.timestamp
    self.vp_ip
    self.vp_asn
```

You can print the message using:

```python
str(msg)
```

Output format:

```
TIMESTAMP|MSG_TYPE|VP_ASN|VP_IP|PREFIXES|ASPATH|COMMUNITIES|ORIGIN|NEXTHOP
```
---

## ⚠️ Error Handling

* `WebsocketConnectionError`: Failed to connect (invalid key, duplicate sessions, etc.)
* `PrefixToAPIKeyError`: Association failure (e.g., malformed prefix list)

---

## 🐞 Debugging

`BGProutesWebsocketClient` includes built-in debugging support with the following methods:

* `set_debug_level(level)` — Set the verbosity level. Available options:

  * `DEBUG_NOTHING` (default)
  * `DEBUG_ESSENTIAL`
  * `DEBUG_EXHAUSTIVE`
  * `DEBUG_TOO_MUCH`

* `set_debug_file(filepath)` — Redirect logs to a specified file. Default is standard error (STDERR).

#### Example

```python
from pybgprouteslive import BGProutesWebsocketClient, DEBUG_TOO_MUCH
import os

client = BGProutesWebsocketClient(os.environ["BGP_API_KEY"])
client.set_debug_level(DEBUG_TOO_MUCH)
client.set_debug_file("/path/to/debug/file.log")
```

---

## Example Scripts

In the example directory, we provide a few examples that illustrate how to our Python client.
You can use them as an example. Feel free to customize them for your own use case.

---

### ⚖️ Rate Limits

Each API key may be associated with up to **10 prefixes**. If you require more, please [contact us](mailto:contact@bgproutes.io) to discuss your use case.

---

## 📄 License

GPLv3

---

## 📬 Contact

For bug reports, suggestions, or support:

📧 [contact@bgproutes.io](mailto:contact@bgproutes.io)

Thank you for using BGProutes.io! 🌐
