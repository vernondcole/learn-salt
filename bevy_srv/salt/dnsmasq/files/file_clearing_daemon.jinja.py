#!/usr/bin/env python3
"""
Runs for a long time, looking for an http query from a recently initialized
computer. When it gets the packet, it tries to clear away the PXE boot configuration
for that computer, so that it will boot from its disk from then on.
"""
from __future__ import print_function
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from pathlib import Path
import time

pillar = NotImplemented  # this file must be processed by Jinja before being run.
HOST_NAME = 'pxe_file_clearing_daemon'
PORT_NUMBER = 4545 # {{ pillar['pxe_clearing_port'] }}
WAIT_TIME = 120 # {{ pillar['pxe_clearing_daemon_life_minutes'] }} * 60  # seconds

BOOT_FROM_DISK_CONFIG_TEXT = '''
default bootfirst
label bootfirst
  say Now booting from disk
  localboot 0
'''

class StoppableHTTPServer(HTTPServer):
    def run(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()

# HTTPRequestHandler class
class File_Clearing_RequestHandler(BaseHTTPRequestHandler):

    # GET
    def do_GET(self):
        print('got request "{}"'.format(self.path))
        work_is_done = False
        job_list = self.server.job_list
        if self.path == '/ping':
            self.send_response_only(200, 'pong')
        else:
            args = self.path.strip().split('?')
            if len(args) < 2 or (args[0] == '/store' and len(args) < 3):
                self.send_error(400, 'Data too short',
                                'Not enough information in query "{}"'.format(self.path))
            elif args[0] == '/store':
                key = args[1]  # MAC address of client
                path = args[2]  # path to configuration file
                job_list[key] = path
                # Send response status code
                self.send_response(201)  # resource created
            elif args[0] == '/clear':
                key = args[1]
                try:
                    config_file = Path(job_list[key])
                    with config_file.open('w') as out:
                        out.write(BOOT_FROM_DISK_CONFIG_TEXT)
                        self.send_response(200)
                    job_list.pop(key)
                    if len(job_list) == 0:
                        print('All candidates cleared.')
                        work_is_done = True
                except OSError as e:
                    print('Error writing file {} --> {}'.format(config_file, e))
                    self.send_error(400, 'OSError', e)
                except KeyError:
                    self.send_error(400, 'IndexError', 'Key {} is unknown.'.format(key))
            else:
                self.send_error(400, 'Bad query', 'Query neither "/store?" nor "/clear?"')

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send message back to client
        message = '<body>Received query "{}".\n</body></html>'.format(self.path)
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))

        if work_is_done:
            time.sleep(5)
            self.server._BaseServer__shutdown_request = True
        return


def timed_shutdown(httpserver):
    print('Timer expired, shutting down.')
    httpserver.shutdown()
    time.sleep(10)



def run(port_number=PORT_NUMBER):
    print("Starting server - %s:%s" % (HOST_NAME, port_number))

    try:
        server_address = ('0.0.0.0', port_number)
        httpd = StoppableHTTPServer(server_address, File_Clearing_RequestHandler)
    except OSError as e:
        if e.errno == 98:
            print('Port {} already in use.'.format(port_number))
            httpd = None
        else:
            raise
    if httpd:
        httpd.job_list = {}
        game_over = threading.Timer(WAIT_TIME, timed_shutdown, (httpd,))
        game_over.start()
        print('running server...')
        server = threading.Thread(None, httpd.run)
        server.start()

        server.join()
        print("Server Stopped - %s:%s" % (HOST_NAME, port_number))
        game_over.cancel()
    else:
        print('Could not create a server.')
        exit(1)


if __name__ == '__main__':
    run()
