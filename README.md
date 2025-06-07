# BGProutes Live Data Documentation

Welcome to **BGProutes.io**, your efficient gateway for accessing **real-time BGP routing data**. This service provides authenticated users with low-latency streams of BGP messages related to their specified prefixes.

The WebSocket server is available at:

```
wss://websocket.bgproutes.io
```

It operates over port 443 and connects clients to data streams for prefixes of interest, sourced from our global network of BGP collectors.

---

## Overview of the Data Pipeline

Our backend uses Apache Kafka to manage and deliver BGP messages. When a user connects via WebSocket using their API key, the server subscribes to the appropriate Kafka topics to stream messages corresponding to their selected prefixes.

> **Note:** This project is in active development. Temporary service interruptions or bugs may occur.

---

## WebSocket Usage Guide

The WebSocket server is accessible at:

```
wss://websocket.bgproutes.io
```

We aim to make the connection process as smooth as possible — it might look long here, but it's quick in practice! For even faster integration, consider using our [Python client](https://github.com/bgproutes-io/pybgprouteslive/).

### 🔐 Authentication

Each WebSocket session requires an **API key**, which must be associated with the prefixes you wish to monitor.

1. Log in to [BGProutes.io](https://bgproutes.io).
2. Navigate to the **API Key** section.
3. Generate an API key and associate it with a **comma-separated list** of prefixes:

   ```
   192.23.62.0/24,2a06:3040:10::/48
   ```

   You may also generate a key with no prefixes initially.

> **Important:** Your API key is **not stored** on our servers. Save it securely — it cannot be recovered.

API key–prefix associations expire after **4 hours** of inactivity (only the prefixes are cleared; the key remains valid).

### 🛠 Alternative Prefix Management

You can also manage your prefixes programmatically via our Live Manager API:

```
https://live-manager-api.bgproutes.io/update_live_prefixes?api_key=YOUR_API_KEY&new_pfxs=PREFIXES
```

Example:

```bash
curl "https://live-manager-api.bgproutes.io/update_live_prefixes?api_key=MY_KEY&new_pfxs=192.23.62.0/24,2a06:3040:10::/48"
```

Again, our [Python client](https://github.com/bgproutes-io/pybgprouteslive/) makes this even easier.

### 🔌 Connecting to the WebSocket

Once your key is ready and associated with prefixes, connect to:

```
wss://websocket.bgproutes.io/?api_key=YOUR_API_KEY
```

### ⚖️ Rate Limits

Each API key may be associated with up to **10 prefixes**. If you require more, please [contact us](mailto:contact@bgproutes.io) to discuss your use case.

---

## Python Client Guide

To simplify integration, we provide a client library: [pybgprouteslive](https://github.com/bgproutes-io/pybgprouteslive/).

### 📦 Installation

```bash
git clone https://github.com/bgproutes-io/pybgprouteslive.git
cd pybgprouteslive
python3 -m pip install .
```

> Dependencies: `websocket-client` and `requests`. Avoid conflicts with `websockets` by using a virtual environment.

### 🧠 Main Components

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

### ⚠️ Error Handling

* `WebsocketConnectionError`: Failed to connect (invalid key, duplicate sessions, etc.)
* `PrefixToAPIKeyError`: Association failure (e.g., malformed prefix list)

### 📬 `BGPLiveMsg` Object

Represents a BGP message with fields like:

```python
class BGPLiveMsg:
    self.isMessageOK
    self.record_type      # "U" for update, "W" for withdraw
    self.prefixes
    self.aspath
    self.communities
    self.nexthop
    self.origin
    self.timestamp
    self.vp_ip, self.vp_asn
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

### 🐞 Debugging

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

### 🔄 Monitor AS Origin Changes

```python
from pybgprouteslive import BGProutesWebsocketClient, MESSAGE_TYPE_ANNOUNCE
import os

REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"
ribs = {}

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
```

### 👀 Track Prefix Visibility

```python
from pybgprouteslive import BGProutesWebsocketClient, MESSAGE_TYPE_ANNOUNCE, MESSAGE_TYPE_WITHDRAW
import os

REQUIRED_PREFIX = "192.23.62.0/24,2a06:3040:10::/48"
ribs = {}

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
```

---

## 📄 License

GPLv3

---

## 📬 Contact

For bug reports, suggestions, or support:

📧 [contact@bgproutes.io](mailto:contact@bgproutes.io)

Thank you for using BGProutes.io! 🌐
