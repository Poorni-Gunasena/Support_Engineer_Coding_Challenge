import http.server
import json
from urllib.parse import urlparse

class APIHandler(http.server.BaseHTTPRequestHandler):
    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/api/create_user':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                if not data.get("email"):
                    self._send_json_response(400, {"error": "Email is required"})
                else:
                    self._send_json_response(201, {"message": f"User {data['email']} created successfully"})
            except json.JSONDecodeError:
                self._send_json_response(400, {"error": "Invalid JSON data"})
        else:
            self._send_json_response(404, {"error": "Not Found"})

def run(server_class=http.server.HTTPServer, handler_class=APIHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"HTTP mock server listening on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run()