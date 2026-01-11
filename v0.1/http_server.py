import threading
import socketserver
from http.server import SimpleHTTPRequestHandler
import json
from shared_state import telemetry_lock, gps_history

HTTP_PORT = 8005
MAP_POLL_INTERVAL = 1.5  # seconds (browser poll)
MAP_FILENAME = "cansat_flight_map.html"

POLL_MS = int(MAP_POLL_INTERVAL * 1000)

MAP_HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>CANSAT Live Map</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <style>html,body,#map{height:100%;margin:0;padding:0}</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
let map = L.map('map').setView([50.85, 4.35], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
  maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
let poly = L.polyline([], {color: 'red'}).addTo(map);
let lastMarker = null;
async function fetchPoints(){
  try {
    const res = await fetch('/points.json');
    if(!res.ok) return;
    const data = await res.json();
    if(!data || !data.lat || data.lat.length===0) return;
    const lat = data.lat;
    const lon = data.lon;
    const pts = [];
    for(let i=0;i<lat.length;i++){ pts.push([lat[i], lon[i]]); }
    poly.setLatLngs(pts);
    if(pts.length>0){
      const last = pts[pts.length-1];
      if(lastMarker) map.removeLayer(lastMarker);
      lastMarker = L.circleMarker(last, {radius:6, color:'green'}).addTo(map);
      map.setView(last, map.getZoom());
    }
  } catch(e){ console.log('fetchPoints error', e); }
}
setInterval(fetchPoints, __POLL_MS__);
fetchPoints();
</script>
</body>
</html>
"""

MAP_HTML = MAP_HTML_TEMPLATE.replace("__POLL_MS__", str(POLL_MS))

class MapRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/map.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(MAP_HTML.encode('utf-8'))
            return
        if self.path == '/points.json':
            with telemetry_lock:
                lat = list(gps_history["lat"])
                lon = list(gps_history["lon"])
            payload = {"lat": lat, "lon": lon}
            b = json.dumps(payload).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        self.send_error(404, "Not Found")

def start_http_server(port=HTTP_PORT):
    server = socketserver.ThreadingTCPServer(('0.0.0.0', port), MapRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"HTTP map server started at http://127.0.0.1:{port}/map.html")
    return server
