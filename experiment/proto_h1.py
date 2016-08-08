# -*- coding: utf-8 -*-
"""
HTTP/1.1 Protocol
~~~~~~~~~~~~~~~~~

This is a wrapper to Nathaniel Smith's h11 library that converts that library
into something that can use the interfaces defined in this experiment.
"""
import h11

from .data_types import Response


class DataHandler(object):
    """
    This object is a HTTP/1.1 DataHandler. It is a basic object capable of
    converting requests into bytes, and bytes into responses.
    """
    def __init__(self):
        self._conn = h11.Connection(h11.CLIENT)
        self._response = None

    def request_to_bytes(self, request):
        """
        Converts a request object to a generator of bytes.
        """
        request_headers = request.headers
        request_headers.append((b'Host', request.host))

        h11_request = h11.Request(
            method=request.method,
            target=request.path,
            headers=request_headers,
        )
        request_bytes = self._conn.send(h11_request)
        yield request_bytes

        if request.body:
            # TODO: Request bodies.
            raise RuntimeError("Bodies not supported yet.")

        return

    def receive_bytes(self, data):
        """
        Receives some bytes. Returns either a Request object or nothing.

        For now this doesn't handle streaming bodies: it preloads all bodies.
        """
        events = self._conn.receive_data(data)

        for event in events:
            if isinstance(event, h11.InformationalResponse):
                # TODO: Handle informational responses.
                pass
            elif isinstance(event, h11.Response):
                self._build_response(event)
            elif isinstance(event, h11.Data):
                self._response.body += event.data
            elif isinstance(event, h11.EndOfMessage):
                return self._response
            elif isinstance(event, h11.ConnectionClosed):
                # This is an unexpected condition.
                raise RuntimeError("Connection closed unexpected.")
            else:
                raise RuntimeError("Unexpected event: %s." % event)

        return None

    def _build_response(self, event):
        """
        Given a single h11 Response event, convert it into our own response.
        """
        self._response = Response(
            code=event.status_code,
            headers=event.headers,
            body=b''
        )
