# -*- coding: utf-8 -*-
"""
Data Types
~~~~~~~~~~

The sync/async experiment is based upon the notion of having data-only objects
that represent all parts of the HTTP semantic layer. These objects are built
and mutated by the upper layers of the experiment in order to generate the
requests and consume the responses. They can then be passed to the
serialization layer, which turns requests into bytes, and bytes into responses.
Finally, these bytes are passed to the communication layers, which are
responsible for actually sending and receiving them.

What is critical is that everything except the communication layers are just
synchronous function calls with no waiting. This means the question of how
concurrency works is driven only by the backend.

Unanswered questions:

- What request body types to we accept? How do we stream them?
- How do we stream a response body?
- What is the type of a response body?
- What is the expected interface of a response body?
"""


class Request(object):
    """
    This is a skeleton semantic representation of a request. We'll flesh it
    out later.
    """
    def __init__(self):
        self.method = b'GET'
        self.host = b'http2bin.org'
        self.path = b'/get'
        self.headers = [(b'user-agent', b'sync-async-experiment/0.0.0')]
        self.body = b''


class Response(object):
    """
    This is a skeleton semantic representation of a response. We'll flesh it
    out later.
    """
    def __init__(self, code, headers, body):
        self.code = code
        self.headers = headers
        self.body = body
