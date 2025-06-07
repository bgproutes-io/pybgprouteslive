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

### pybgprouteslive class

### Examples

### Licence


# Final thoughs
