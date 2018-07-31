# @Author: Bartosz Nowakowski
# @Github: https://github.com/rolzwy7
#
# Copyright (c) 2018
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Requests
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
import requests

# Parsing and Printing
import json
import pprint as pp

# Time
from email import utils
import datetime
import time

# Config
class MGApiConfiguration():

    def __init__(self):
        self._DEBUG = True
        self._DEBUG_SIGN = "[DEBUG]"
        self._API_USER = "api"
        self._REQUEST_TIMEOUT_SECONDS = 7


        self._EVENTS = [
            "accepted",
            "delivered",
            "failed",
            "opened",
            "clicked",
            "unsubscribed",
            "complained",
            "stored"
        ]
        self._RESOLUTIONS = [
            "hour",
            "day",
            "month"
        ]
    def printConfig(self):
        print("[Mailgun API Client - Configuration]")
        print("Debug:", self._DEBUG)
# Logging
class MGApiLogging(MGApiConfiguration):
    def printer_print(self, sign, *argv):
        """
            Extended print
        """
        dayname, month, daynum, hour, year = time.asctime().split(" ")
        to_print_time = " ".join([dayname, month, year, daynum, hour])
        print("[%s]" % to_print_time, sign, end=" ")
        for e in argv:
            print(e, end=" ")
        print("")

    def print_debug(self, *argv):
        """
            Print if in debug mode ( _DEBUG == True )
        """
        if self._DEBUG: self.printer_print("[DEBUG]", *argv)

    def print_debug_pretty(self, obj):
        """
            Print ( use pprint.pprint ) if in debug mode ( _DEBUG == True )
        """
        if self._DEBUG: pp.pprint(obj)
# Helper methods
class MGApiUtils(MGApiLogging):
    # Justification methods
    def justify(self, json_object, msg, success=True, reason=""):
        """
            summary:
                add justification to response
            params:
                json_object - response in json format
                msg         - message
                success     - indicator of success or failure
                reason      - justification of error
            returns: (1 value/s)
                json_object with added justification
        """
        json_object["justify"] = {
            "success": success,
            "reason": reason,
            "msg": msg
        }
        return json_object
    def not_in_justify(self, what, not_in, caller="<not_set>", reason="<not_set>", success=False):
        """
            summary:
                returns justification if key isn't present in dict
            params:
                what - key name
                not_in - dictionary
                caller - caller method
                reason - reason of error
                success - indicator of success or failure
            returns: (2 value/s)
                deserialized and serialized json
                    or
                False ,False
        """
        if what not in not_in:
            deserialized = {}
            deserialized = self.justify(
                deserialized,
                "Operation failed: {caller}".format(caller=caller),
                success=success,
                reason=reason
            )
            return deserialized, self.serialize_json(deserialized)
        return False, False
    # JSON parsing methods
    def serialize_json(self, json_object, sort_keys=True, indent=4, separators=(',', ': ')):
        """
        docs:
            https://docs.python.org/3/library/json.html
        summary:
            Returns serialized json (api response)
        params:
            json_object  - json api response
            sort_keys    - json.dumps param (see documentation)
            indent       - json.dumps param (see documentation)
            separators   - json.dumps param (see documentation)
        returns: (1 value/s)
            serialized json (api response)
        """
        return json.dumps(json_object, sort_keys=sort_keys, indent=indent, separators=separators)
    def deserialize_json(self, json_string):
        """
        docs:
            https://docs.python.org/3/library/json.html
        summary:
            Returns deserialized json (api response)
        params:
            json_string - json string (api response)
        returns: (1 value/s)
            deserialized json (api response)
        """
        if not isinstance(json_string, str) and not isinstance(json_string, bytes):
            print("implement this: helpers deserialize_json method")
        if isinstance(json_string, bytes):
            json_string = str(json_string, "utf8") if isinstance(json_string, bytes) else string
        return json.loads(json_string)
    def to_json(self, json_string):
        """
        docs:
            https://docs.python.org/3/library/json.html
        summary:
            Returns serialized and deserialized json_string (api response).
            Adds justification to response.
            justification is always success=True with appropriate message

            DON'T use this method for deserialization and serialization
            of json object/json string instead use together:
                serialize_json method
                    and
                deserialize_json method
        params:
            json_string - api response
        returns: (2 value/s)
            Serialized and deserialized json (api response)
        """
        deserialized = self.deserialize_json(json_string=json_string)
        # Add justification.
        deserialized = self.justify(deserialized, "Operation succeeded.")
        serialized   = self.serialize_json(deserialized)
        return deserialized, serialized
    # Options modifiers methods (Sending)
    def options_add_header(self, options, header, value):
        """
        docs:
            https://documentation.mailgun.com/en/latest/api-sending.html#sending
        summary:
            adds new element to options dictionary
        params:
            options - dictionary
            header - key
            value - value
        returns: (1 value/s)
            dictionary (options param) with added new element
        """
        options["h:{header}".format(header=header)] = value
        return options
    def options_add_variable(self, options, variable, value):
        """
        docs:
            https://documentation.mailgun.com/en/latest/api-sending.html#sending
        summary:
            adds new element to options dictionary
        params:
            options - dictionary
            header - key
            value - value
        returns: (1 value/s)
            dictionary (variable param) with added new element
        """
        options["v:{variable}".format(variable=variable)] = value
        return options
    # Time
    def nowRFC2822(self, days=0, hours=0, minutes=0, return_timestamp=False):
        """
        docs:
            https://documentation.mailgun.com/en/latest/api-sending.html#sending
        summary:
            adds new element to options dictionary
        params:
            days - [integer] number of days
            hours - [integer] number of days
            minutes - [integer] number of days
            return_timestamp - Bool
        returns: (1 value/s or 2 value/s)
            RFC2822 datetime
                or
            RFC2822 datetime and it's timestamp
        """
        timedelta_shift = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        now_datetime = datetime.datetime.now() + timedelta_shift
        now_timestamp = time.mktime(now_datetime.timetuple())
        # localtime=True (Sets local timezone)
        result = utils.formatdate(now_timestamp, localtime=True)
        self.print_debug("timedelta_shift:", timedelta_shift)
        self.print_debug("now_datetime:", now_datetime)
        self.print_debug("now_timestamp:", now_timestamp)
        self.print_debug("result:", result)
        if return_timestamp:
            return result, now_timestamp
        return result
# Unification of request responses
class MGApiRequests(MGApiUtils):

    # RequestExtended
    def requestEx(self, url, request_function, request_params):
        """
        summary:
            requests.request but with overkill exceptions and
            option of choosing type of request
        params:
            url - URL of the api endpoint
            request_function - method from one below:
                                    self.get
                                    self.post
                                    self.put
            request_params - parameters of chosen 'request_function'
        returns: (3 value/s)
            reason - reason for exception
            success - indicator of success (Bool)
            result - result of request
        """
        timeout = self._REQUEST_TIMEOUT_SECONDS
        request_params_common = {
            "auth": (self.api_user, self.private_key),
            "timeout": timeout
        }
        request_params = {**request_params, **request_params_common}

        reason = None
        success = None
        result = None

        try:
            result = request_function(url, **request_params)
            if result.status_code != 200:
                deserialized_content = self.deserialize_json(result.content)
                reason = "Status code:{status_code} | Message:{message} | Content:{content}".format(
                    status_code=result.status_code,
                    message=deserialized_content["message"] if "message" in deserialized_content.keys() else "KeyError",
                    content=result.content
                )
                success, result = False, None
            else:
                # operation succeeded
                reason, success, result = None, True, result
        except Timeout as e:
            reason, success, result = "Timeout: {exception}".format(exception=e), False, None
        except ConnectionError as e:
            reason, success, result = "ConnectionError: {exception}".format(exception=e), False, None
        except Exception as e:
            reason, success, result = "Unhandled Exception: {exception}".format(exception=e), False, None

        return reason, success, result

    # Requests
    def get(self, url, params={}, **kwargs):
        """
        docs:
            http://docs.python-requests.org/en/master/
        summary:
            Method used as requestEx method's parameter
        params:
            url - URL of the api endpoint
            params - GET parameters
        returns: (3 value/s)
            reason - reason for exception
            success - indicator of success (Bool)
            result - result of request
        """
        request_function = requests.get
        request_params = {
            "params": params,
            **kwargs
        }
        self.print_debug("MGApiRequests.get", request_params);
        reason, success, result = self.requestEx(url, request_function, request_params)
        return reason, success, result
    def post(self, url, data={}, **kwargs):
        """
        docs:
            http://docs.python-requests.org/en/master/
        summary:
            Method used as requestEx method's parameter
        params:
            url - URL of the api endpoint
            data - POST data
        returns: (3 value/s)
            reason - reason for exception
            success - indicator of success (Bool)
            result - result of request
        """
        request_function = requests.post
        request_params = {
            "data": data,
            **kwargs
        }
        self.print_debug("MGApiRequests.post", request_params);
        reason, success, result = self.requestEx(url, request_function, request_params)
        return reason, success, result
    def put(self, url, data={}, **kwargs):
        """
        docs:
            http://docs.python-requests.org/en/master/
        summary:
            Method used as requestEx method's parameter
        params:
            url - URL of the api endpoint
            data - PUT data
        returns: (3 value/s)
            reason - reason for exception
            success - indicator of success (Bool)
            result - result of request
        """
        request_function = requests.put
        request_params = {
            "data": data,
            **kwargs
        }
        self.print_debug("MGApiRequests.put", request_params);
        reason, success, result = self.requestEx(url, request_function, request_params)
        return reason, success, result

    def parseResponse(self, reason, success, result, caller=""):
        """
        summary:
            Judges if request was success by success parameter
        params:
            reason - reason for exception
            success - indicator of success (Bool)
            result - result of request
            caller - caller method
        returns: (2 value/s)
            deserialized and serialized json
        """
        # Success
        if success:
            # Calling self.to_json should only occur when request
            # is considered to be success=True
            deserialized, serialized = self.to_json(result.content)
            return deserialized, serialized
        # Error
        deserialized = {}
        deserialized = self.justify(
            deserialized,
            "Operation failed: {caller}".format(caller=caller),
            success=success,
            reason=reason
        )
        return deserialized, self.serialize_json(deserialized)
# Api
class Api(MGApiRequests):
    def __init__(self, base_url, domain, private_key):
        MGApiConfiguration.__init__(self)
        self.base_url    = base_url
        self.domain      = domain
        self.private_key = private_key
        self.api_user    = self._API_USER

    # Pagination
    def follow_pagination(self, deserialized_response):
        """
        summary:
            Follows pagination until items array lenght is 0
        params:
            deserialized_response - deserialized json (api response)
        returns: (3 value/s)
            exhausted - indicates that there is no items left
            deserialized - deserialized json
            serialized - serialized json
        """
        exhausted = False
        # Check if paging key exists
        deserialized, serialized = self.not_in_justify(
            "paging",
            deserialized_response.keys(),
            caller="Api.follow_pagination",
            reason="KeyError 'paging'",
            success=False
        )
        if deserialized and serialized:
            return exhausted, deserialized, serialized
        # Check if next key exists
        deserialized, serialized = self.not_in_justify(
            "next",
            deserialized_response["paging"].keys(),
            caller="Api.follow_pagination",
            reason="KeyError 'next' in paging",
            success=False
        )
        if deserialized and serialized:
            return exhausted, deserialized, serialized

        url = deserialized_response["paging"]["next"]
        reason, success, result = self.get(url, params={})
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.follow_pagination")

        exhausted = True if len(deserialized["items"]) == 0 else False
        return exhausted, deserialized, serialized

    # Domains
    def get_domains(self, domain="", limit=100, skip=0):
        """
            GET /domains/<domain>
            GET /domains
        """
        url = "{base_url}/domains".format(base_url=self.base_url)
        if domain:
            url = "{url}/{domain}".format(url=url, domain=domain)
        # Optional prameters
        params = {"limit": limit, "skip": skip}
        reason, success, result = self.get(url, params=params)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.get_domains")
        return deserialized, serialized

    # Supressions (method used by get_bounces, get_unsubscribes and get_complaints)
    def get_supressions(self, get_what, address="", domain="", limit=100, caller="<not_set>"):
        """
        summary:
            DRY for get_bounces, get_complaints and get_unsubscribes
        params:
            get_what - {bounces, complaints, unsubscribes}
            address - email address
            domain - domain name
            limit - limit of items returned
            caller - caller method
        returns: (2 value/s)
            deserialized - deserialized json
            serialized - serialized json
        """
        # Set default if invalid limit value
        if limit < 0 or limit > 10000: limit = 100;
        # If domain is set use it else use domain from constructor
        cp_domain = domain if domain else self.domain
        url = "{base_url}/{domain}/{get_what}".format(base_url=self.base_url, domain=cp_domain, get_what=get_what)
        if address:
            url = "{url}/{address}".format(url=url, address=address)
        # Optional prameters
        params = {"limit": limit}
        reason, success, result = self.get(url, params=params)
        deserialized, serialized = self.parseResponse(reason, success, result, caller=caller)
        return deserialized, serialized
    # Bounces
    def get_bounces(self, address="", domain="", limit=100):
        """
            GET /<domain>/bounces
            GET /<domain>/bounces/<address>
        """
        deserialized, serialized = self.get_supressions(
            "bounces",
            address=address,
            domain=domain,
            limit=limit,
            caller="Api.get_bounces"
        )
        return deserialized, serialized
    # Unsubscribes
    def get_unsubscribes(self, address="", domain="", limit=100):
        """
            GET /<domain>/unsubscribes
            GET /<domain>/unsubscribes/<address>
        """
        deserialized, serialized = self.get_supressions(
            "unsubscribes",
            address=address,
            domain=domain,
            limit=limit,
            caller="Api.get_unsubscribes"
        )
        return deserialized, serialized
    # Complaints
    def get_complaints(self, address="", domain="", limit=100):
        """
            GET /<domain>/complaints
            GET /<domain>/complaints/<address>
        """
        deserialized, serialized = self.get_supressions(
            "complaints",
            address=address,
            domain=domain,
            limit=limit,
            caller="Api.get_complaints"
        )
        return deserialized, serialized

    # Mailing Lists
    def get_lists(self, address="", limit=100):
        """
            GET /lists/<address>
            GET /lists/pages
        """
        url = "{base_url}/lists".format(base_url=self.base_url)
        url = "{url}/{address}".format(url=url, address=address) if address else "{url}/pages".format(url=url)
        # Optional prameters
        params = {"limit": limit}
        reason, success, result = self.get(url, params=params)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.get_lists")
        return deserialized, serialized
    def add_list(self, address, name="", description="", access_level="readonly"):
        """
            POST /lists
        """
        url = "{base_url}/lists".format(base_url=self.base_url)
        data = {
            "address": address,
            "name": name,
            "description": description,
            "access_level": access_level
        }
        reason, success, result = self.post(url, data=data)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.add_list")
        return deserialized, serialized
    def get_members(self, address, member_address="", limit=100, subscribed=None):
        """
            GET /lists/<address>/members/<member_address>
            GET /lists/<address>/members/pages
        """
        url = "{base_url}/lists/{address}/members".format(base_url=self.base_url, address=address)
        url = "{url}/{member_address}".format(url=url, member_address=member_address) if member_address else "{url}/pages".format(url=url)
        # Optional prameters
        params = {"limit": limit}
        if subscribed is not None:
            params["subscribed"] = subscribed
        reason, success, result = self.get(url, params=params)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.get_members")
        return deserialized, serialized
    def bulk_add_members(self, address, members, upsert="no"):
        """
            POST /lists/<address>/members.json
        """
        url = "{base_url}/lists/{address}/members.json".format(base_url=self.base_url, address=address)
        members_json_string = self.serialize_json(members)
        data = {
            "members": members_json_string,
            "upsert": upsert
        }
        reason, success, result = self.post(url, data=data)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.bulk_add_members")
        return deserialized, serialized

    # Events
    def ret_events_filter_fields(self):
        """

        """
        ret = {
            "event": None,
            "list": None,
            "attachment": None,
            "from": None,
            "message-id": None,
            "subject": None,
            "to": None,
            "size": None,
            "recipient": None,
            "tags": None,
            "severity": None
        }
        return ret
    def get_events(self, domain="", begin="", end="", ascending="yes", limit=300, filter_fields={}):
        """
            GET /<domain>/events
        """
        limit = 100 if limit<0 or limit>300 else limit
        # If domain is set use it else use domain from constructor
        cp_domain = domain if domain else self.domain
        url = "{base_url}/{domain}/events".format(base_url=self.base_url, domain=cp_domain)
        # Optional prameters
        params = {
            "limit": limit
        }
        if begin:     params["begin"] = begin;
        if end:       params["end"] = end;
        if ascending: params["ascending"] = ascending;
        for key, value in filter_fields.items():
            if value is not None: params[key] = value;
        reason, success, result = self.get(url, params=params)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.get_events")
        return deserialized, serialized

    # Stats
    def get_stats_total(self, event, domain="", start="", end="", resolution="day", duration=""):
        """
            GET /<domain>/stats/total
        """
        # Check if event is valid
        deserialized, serialized = self.not_in_justify(
            event,
            self._EVENTS,
            caller="Api.get_stats_total",
            reason="Event name is not valid: {event}".format(event=event),
            success=False
            );
        if deserialized and serialized:
            return deserialized, serialized
        # Check if resolution is valid
        deserialized, serialized = self.not_in_justify(
            resolution,
            self._RESOLUTIONS,
            caller="Api.get_stats_total",
            reason="Resolution is not valid: {resolution}".format(resolution=resolution),
            success=False
            );
        if deserialized and serialized:
            return deserialized, serialized

        # If domain is set use it else use domain from constructor
        cp_domain = domain if domain else self.domain
        params = {
            "event": event,
            "resolution": resolution
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if duration:
            params["duration"] = duration

        url = "{base_url}/{domain}/stats/total".format(base_url=self.base_url, domain=cp_domain)
        reason, success, result = self.get(url, params=params)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.get_stats_total")
        return deserialized, serialized

    # Sending
    def ret_additional_sending_options(self, tracking=True, testmode=False):
        """
            return additional sending option
        """
        additional_options = {
            "cc": None,
            "bcc": None,
            "attachment": None,
            "inline": None,
            "o:tag": [],
            "o:dkim": None,
            "o:deliverytime": None,
            "o:testmode": None,
            "o:tracking": None,
            "o:tracking-clicks": None,
            "o:tracking-opens": None,
            "o:require-tls": None,
            "o:skip-verification": None
        }
        if testmode:
            additional_options["o:testmode"] = "yes"
        if tracking:
            additional_options["o:tracking"]        = "yes"
            additional_options["o:tracking-clicks"] = "yes"
            additional_options["o:tracking-opens"]  = "yes"

        return additional_options
    def send_single_message(self, From, to, subject, html, text, domain="", additional_sending_options=None):
        """
            POST /<domain>/messages
        """
        # If domain is set use it else use domain from constructor
        cp_domain = domain if domain else self.domain
        # Set default additional_sending_options if not set by user
        if additional_sending_options is None:
            additional_sending_options = self.ret_additional_sending_options()
        # debug
        self.print_debug("Api.send_single_message", "PARAM additional_sending_options")
        self.print_debug_pretty(additional_sending_options)
        data = {
            "from": From, "to": to,
            "subject": subject, "html": html, "text": text
        }
        for key, value in additional_sending_options.items():
            if value is not None:
                data[key] = value
        # debug
        self.print_debug("Api.send_single_message", "POST data")
        self.print_debug_pretty(data)
        # Actual sending
        url = "{base_url}/{domain}/messages".format(base_url=self.base_url, domain=cp_domain)

        reason, success, result = self.post(url, data=data)
        deserialized, serialized = self.parseResponse(reason, success, result, caller="Api.send_single_message")
        return deserialized, serialized
