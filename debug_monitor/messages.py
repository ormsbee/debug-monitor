"""
This module is responsible for holding the state of everything we know about the
servers that are reporting in, the requests/responses, and everything associated
with them. It does _not_ hold UI state (e.g. "what row is selected"), as that
will live in the app module.
"""
from asyncio import Lock
from collections import defaultdict


class MessageLog:
    
    def __init__(self):
        # { request_uuid_str : { sender: data }}
        self.lock = Lock()

        self.requests = defaultdict(dict)

        # Try this one indexed by sender first
        self.requests_by_sender = defaultdict(dict)

        # this is hacky temp measure to test the UI
        self.last_request_uuid_reported = None

    def add_message(self, request_uuid, sender, data):
        # We'll need an append structure. Can use a different message flag for
        # that.
        if request_uuid is None:  # eventually we might handle system stuff here, but not yet
            return

    #    async with self.lock:
        self.requests[request_uuid][sender] = data
        self.requests_by_sender[sender][request_uuid] = data
        self.last_request_uuid_reported = request_uuid

    def get_message(self, request_uuid, sender):
        return self.requests[request_uuid].get(sender)

        # return self.requests_by_sender[sender].get(request_uuid)


    def get_messages(self, num):
        # Iterate the requests in reverse and take the first {num}, to get the
        # most recent requests.
        return self.requests.items()

        most_recent_requests = list(reversed(self.requests.items())[:num])

        # Then reverse that to give the messages in order from oldest to newest.
        return list(reversed(most_recent_requests))
