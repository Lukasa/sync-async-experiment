# -*- coding: utf-8 -*-
"""
The Synchronous Runner
~~~~~~~~~~~~~~~~~~~~~~

The synchronous runner is a backend for the sync/async experiment that provides
a "run until complete"-like interface for entirely synchronous code.
Essentially, it does not actually yield the flow of control to an event loop:
instead, it entirely synchronously steps through the I/O.

To do this, it takes an object that it can repeatedly call ``next()`` on, which
will provide bytes each time that ``next()`` call is made, and returns a
generator. This generator is used essentially as a coroutine: each time
``next()`` is called, the generator will issue a call to ``select()``. The
``select()`` call has four possible outcomes:

1. timeout, which will yield an exception. This allows the calling code to make
   a decision about whether to consider the timeout a problem or not.
2. socket readable, in which case the code will issue a read and yield the
   read bytes.
3. socket writeable, in which case the code will call ``next()`` and write the
   returned bytes to the socket.
4. socket closed (readable with empty read), in which case the generator will
   exit.
"""
import select


def socket_send_loop(sock, byte_source, timeout=5):
    """
    The socket sending loop.

    That timeout should be more clever, but for now it'll do.
    """
    rlist = [sock]
    wlist = [sock]
    buffered_bytes = b''
    while True:
        rlist, wlist, _ = select.select([sock], [sock], [], timeout)
        if rlist:
            read_data = sock.recv(8192)
            if not read_data:
                # Socket closed.
                return
            yield read_data
        elif wlist:
            if buffered_bytes:
                data_to_send = buffered_bytes
            else:
                try:
                    data_to_send = next(byte_source)
                except StopIteration:
                    # Sending is done. We should stop checking if the socket is
                    # writeable.
                    wlist = []
                    continue

            sent_bytes = sock.send(data_to_send)
            buffered_bytes = data_to_send[sent_bytes:]


def run(request, data_handler, sock):
    """
    A synchronous request/response sender.

    This method takes a request and a data handler. The request codifies the
    request to be sent.

    The data handler contains most of the intelligence in the code. It is a
    complex object that must have two methods:
    - one that takes a request and returns a generator that builds bytes.
    - one that receives bytes and returns a response object or None.

    This will run the socket loop indefinitely until a response object is
    returned from the data handler.

    This does not yet handle:

    - streaming the response body
    - 100 continue (not clear we should handle that at all)
    - HTTP/2, which has some concerns about this interface
    - plenty of error cases!
    - socket connection
    - connection pooling
    """
    request_generator = data_handler.request_to_bytes(request)
    sock_loop = socket_send_loop(sock, request_generator)

    for byte_chunk in sock_loop:
        response = data_handler.receive_bytes(byte_chunk)
        if response is not None:
            return response
