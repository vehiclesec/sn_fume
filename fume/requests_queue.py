import globals as g
import helper_functions.print_verbosity as pv

def push(request):
    #if len(g.request_queue) == g.REQUEST_QUEUE_SIZE:
    #    g.request_queue.pop(0)
    g.request_queue.append(request)

def print_queue():
    if len(g.request_queue) == 0:
        return

    pv.normal_print("Request queue (starting from most recent):")
    g.request_queue.reverse()
    for index, req in enumerate(g.request_queue):
        pv.normal_print("%d: %s" % (index, req.hex()))
