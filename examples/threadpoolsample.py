#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
from threadpool import *

################
# USAGE EXAMPLE
################

if __name__ == '__main__':
    import random
    import time

    # the work the threads will have to do (rather trivial in our example)
    def do_something(data):
        time.sleep(random.randint(1,5))
        result = round(random.random() * data, 5)
        # just to show off, we throw an exception once in a while
        if result > 5:
            raise RuntimeError("Something extraordinary happened!")
        return result

    # this will be called each time a result is available
    def print_result(request, result):
        print "**** Result from request #%s: %r" % (request.request_id, result)

    # this will be called when an exception occurs within a thread
    # this example exception handler does little more than the default handler
    def handle_exception(request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print request
            print exc_info
            raise SystemExit
        print "**** Exception occured in request #%s: %s" % \
          (request.request_id, exc_info)

    # assemble the arguments for each job to a list...
    data = [random.randint(1,10) for i in range(20)]
    # ... and build a WorkRequest object for each item in data
    requests = make_requests(do_something, data, print_result, handle_exception)
    # to use the default exception handler, uncomment next line and comment out
    # the preceding one.
    #requests = makeRequests(do_something, data, print_result)

    # or the other form of args_lists accepted by makeRequests: ((,), {})
    data = [((random.randint(1,10),), {}) for i in range(20)]
    requests.extend(
        make_requests(do_something, data, print_result, handle_exception)
        #makeRequests(do_something, data, print_result)
        # to use the default exception handler, uncomment next line and comment
        # out the preceding one.
    )

    # we create a pool of 3 worker threads
    print "Creating thread pool with 3 worker threads."
    main = ThreadPool(3)

    # then we put the work requests in the queue...
    for req in requests:
        main.queue_request(req)
        print "Work request #%s added." % req.request_id
    # or shorter:
    # [main.putRequest(req) for req in requests]

    # ...and wait for the results to arrive in the result queue
    # by using ThreadPool.wait(). This would block until results for
    # all work requests have arrived:
    # main.wait()

    # instead we can poll for results while doing something else:
    i = 0
    while True:
        try:
            time.sleep(0.5)
            main.poll()
            print "Main thread working...",
            print "(active worker threads: %i)" % (threading.activeCount()-1, )
            if i == 10:
                print "**** Adding 3 more worker threads..."
                main.create_workers(3)
            if i == 20:
                print "**** Dismissing 2 worker threads..."
                main.dismiss_workers(2)
            i += 1
        except KeyboardInterrupt:
            print "**** Interrupted!"
            break
        except NoResultsPending:
            print "**** No pending results."
            break
    if main.dismissed_workers:
        print "Joining all dismissed worker threads..."
        main.join_all_dismissed_workers()

