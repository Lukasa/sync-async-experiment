# -*- coding: utf-8 -*-
"""
This is a very basic example of the code used in the sync/async experiment.
"""
import socket

from experiment import sync, data_types, proto_h1


def do_something_sync(request):
    s = socket.create_connection((b'http2bin.org', 80))
    data_handler = proto_h1.DataHandler()
    return sync.run(request, data_handler, s)


def main():
    req = data_types.Request()
    resp = do_something_sync(req)
    print(resp.code)
    print(resp.headers)
    print(resp.body)


if __name__ == '__main__':
    main()
