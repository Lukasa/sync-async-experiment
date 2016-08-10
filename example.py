# -*- coding: utf-8 -*-
"""
This is a very basic example of the code used in the sync/async experiment.
"""
import asyncio
import socket

from experiment import sync, data_types, proto_h1
from experiment import asyncio as asyncio_runner

loop = asyncio.get_event_loop()


def do_something_sync(request):
    s = socket.create_connection((b'http2bin.org', 80))
    data_handler = proto_h1.DataHandler()
    return sync.run(request, data_handler, s)


def post_data():
    yield b"key1=val1"
    yield b"&"
    yield b"key2=val2"


@asyncio.coroutine
def async_main():
    print("Running asynchronous runner")
    req = data_types.Request()
    req.method = b'POST'
    req.path = b'/post'
    req.headers.append((b'Content-Type', b'application/x-www-form-urlencoded'))
    req.headers.append((b'Transfer-Encoding', b'chunked'))
    req.body = post_data()
    data_handler = proto_h1.DataHandler()
    resp = yield from asyncio_runner.run(req, data_handler, "http2bin.org", 80)
    print(resp.code)
    print(resp.headers)
    print(resp.body)
    print("Asynchronous runner complete")



def main():
    print("Running synchronous runner")
    req = data_types.Request()
    req.method = b'POST'
    req.path = b'/post'
    req.headers.append((b'Content-Type', b'application/x-www-form-urlencoded'))
    req.headers.append((b'Transfer-Encoding', b'chunked'))
    req.body = post_data()
    resp = do_something_sync(req)
    print(resp.code)
    print(resp.headers)
    print(resp.body)
    print("Synchronous runner complete")


if __name__ == '__main__':
    main()
    loop.run_until_complete(async_main())
