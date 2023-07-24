#nicholas kruzan 7-24-2023
#simple web server to take in dump1090 json data and output kml data
#useful with google earth to have ~4sec live air traffic on google earth pro
#
import simplekml
from urllib.request import urlopen
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os
import sys

#this script directory, used for icon image path
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

#where to get the dump1090 datas
dump1090_server_url = "http://10.1.1.213:8080/data/aircraft.json"

#our server params
this_server_name = "localhost"
this_server_port = 8888

class KMLServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        self.wfile.write(bytes(self.output_kml(), "utf-8"))
    def output_kml(self):
        #get new datas from dump1090
        response = urlopen(dump1090_server_url)
        data_json = json.loads(response.read())
        kml = simplekml.Kml()
        aircraft_no_position = 0
        aircraft_visible = 0
        for aircraft in data_json['aircraft']:
            keys = ["hex","squawk","flight","lat","lon","nucp","seen_pos","altitude","vert_rate","track","speed","messages","seen","rssi"]
            #if any keys missing create empty key
            for key in keys:
                if key not in aircraft:
                    aircraft[key] = ""
            #we only want to output those with position datas
            if aircraft["lat"] != "":
                aircraft_visible += 1
                pnt = kml.newpoint(name=aircraft['flight'], coords=[(aircraft['lon'],aircraft['lat'])], description=pretty_description(aircraft))
                pnt.style.iconstyle.scale = 2  # Icon thrice as big
                #pnt.style.iconstyle.icon.href = "file://"+script_directory+"/icon_mission_airplane.png"
                pnt.style.iconstyle.icon.href = "https://raw.githubusercontent.com/ArduPilot/ArduConfigurator/3776a97e261131ee3b4bc604634a6fbe7dccd478/images/icons/icon_mission_airplane.png"
                pnt.style.iconstyle.heading = aircraft['track']
            else:
                 aircraft_no_position+=1

        print(aircraft_visible, 'aircraft visible. No position for', aircraft_no_position, 'sources.')
        
        return kml.kml()

def pretty_description(aircraft):
            return '''
                hex: {}
                squawk: {}
                flight: {}
                lat: {}
                lon: {}
                nucp: {}
                seen_pos: {}
                altitude: {}
                vert_rate: {}
                track: {}
                speed: {}
                messages: {}
                seen: {}
                rssi: {}
                '''.format( aircraft['hex'],
                            aircraft['squawk'],
                            aircraft['flight'],
                            aircraft['lat'],
                            aircraft['lon'],
                            aircraft['nucp'],
                            aircraft['seen_pos'],
                            aircraft['altitude'],
                            aircraft['vert_rate'],
                            aircraft['track'],
                            aircraft['speed'],
                            aircraft['messages'],
                            aircraft['seen'],
                            aircraft['rssi'] )


if __name__ == "__main__":        
    webServer = HTTPServer((this_server_name, this_server_port), KMLServer)
    print("Server started http://%s:%s" % (this_server_name, this_server_port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")