from http.server import SimpleHTTPRequestHandler, HTTPServer

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>?? Alfa Bridge dziala!</h1><p>Karen Tonoyan - Krolowa Cloud</p>')

print('?? Server starting at http://localhost:8000')
server = HTTPServer(('0.0.0.0', 8000), MyHandler)
server.serve_forever()
