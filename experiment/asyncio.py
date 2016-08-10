# -*- coding: utf-8 -*-
"""
The Asyncio Runner
~~~~~~~~~~~~~~~~~~

The asyncio runner is a backend for the sync/async experiment that provides
an asyncio interface that otherwise matches the sync interface defined
elsewhere.
"""
import asyncio


class _ClientHTTPProtocol(asyncio.Protocol):
    """
    This is a basic HTTP protocol that is used in the sync/async experiment.
    This protocol is used to issue a HTTP request and receive a HTTP response.
    This protocol can potentially be quite long-lived if the connection is
    being actively re-used.
    """
    def __init__(self):
        self.transport = None
        self.data_handler = None
        self._response_future = None

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        # TODO: We need to be somewhat clever here, but right now do nothing.
        pass

    def data_received(self, data):
        response = self.data_handler.receive_bytes(data)
        if response is not None:
            self._response_future.set_result(response)
            self._response_future = None

    @asyncio.coroutine
    def send_request(self, request):
        # TODO: flow control, listen for watermarks and stuff.
        assert self._response_future is None
        self._response_future = asyncio.Future()

        request_bytes = self.data_handler.request_to_bytes(request)
        self.transport.write(request_bytes)

        # For asyncio, the request body can be bytes, or an iterable, or a
        # coroutine function.
        # TODO: Consider restricting to Python 3.5 and allowing async
        # iterables.
        if isinstance(request.body, bytes):
            body = [request.body]
        else:
            body = request.body

        # If the body is a coroutine function, yield from it and then wrap
        # the result in a list so we can iterate over it.
        if asyncio.iscoroutinefunction(body):
            body = yield from body()
            body = [body]

        for chunk in body:
            chunk_bytes = self.data_handler.body_chunk_to_bytes(chunk)
            self.transport.write(chunk_bytes)

        eof_bytes = self.data_handler.end_of_body()
        if eof_bytes:
            self.transport.write(eof_bytes)

        return (yield from self._response_future)


def _client_http_protocol_factory():
    return _ClientHTTPProtocol()


@asyncio.coroutine
def run(request, data_handler, host, port):
    """
    A asyncio request/response sender.

    This method takes a request and a data handler. The request codifies the
    request to be sent.

    The data handler contains most of the intelligence in the code. It is a
    complex object that must have two methods:
    - one that takes a request and returns a generator that builds bytes.
    - one that receives bytes and returns a response object or None.

    This returns a coroutine that yields the flow of execution until the
    response has arrived.

    This does not yet handle:

    - 100 continue (not clear we should handle that at all)
    - HTTP/2, which has some concerns about this interface
    - plenty of error cases!
    - connection pooling
    - flow control
    """
    loop = asyncio.get_event_loop()
    _, protocol = yield from loop.create_connection(
        _client_http_protocol_factory,
        host=host,
        port=port,
    )

    # TODO: We need to be smarter about this. Connection pooling will need to
    # do this too.
    protocol.data_handler = data_handler
    return (yield from protocol.send_request(request))
