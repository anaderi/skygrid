from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/xmlrpc',)

# Create server
server = SimpleXMLRPCServer(("0.0.0.0", 9000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

def get_task():
    return '{"task": "Do Something Useful", "constraints": "immediately"}'

server.register_function(get_task, 'GetTask')
server.serve_forever()

