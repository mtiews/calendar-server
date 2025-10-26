import requests
from icalendar import Calendar
from datetime import datetime, timedelta
import pytz
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

def download_ical(url):
    """Download iCal file from URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading iCal file: {e}")
        return None

def parse_events(ical_data, start_day=0, end_day=2):
    """Parse iCal data and return events between start_day and end_day.
    start_day and end_day are relative to today (0 = today, 1 = tomorrow, etc.)"""
    if not ical_data:
        return []

    # Get today and calculate start and end dates
    today = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    filter_start_date = today + timedelta(days=start_day)
    filter_end_date = today + timedelta(days=end_day)

    events = []
    try:
        cal = Calendar.from_ical(ical_data)
        for component in cal.walk():
            if component.name == "VEVENT":
                start_date = component.get('dtstart').dt
                
                # Convert datetime to UTC for comparison if it's a datetime object
                if isinstance(start_date, datetime):
                    if not start_date.tzinfo:
                        # If the date has no timezone, assume UTC
                        start_date = pytz.UTC.localize(start_date)
                    else:
                        # Convert to UTC for comparison
                        start_date = start_date.astimezone(pytz.UTC)
                else:
                    # If it's just a date, convert to datetime at midnight UTC
                    start_date = datetime.combine(start_date, datetime.min.time())
                    start_date = pytz.UTC.localize(start_date)

                # Check if the event is within the specified date range
                if start_date >= filter_start_date and start_date <= filter_end_date:
                    events.append({
                        'summary': str(component.get('summary', 'No Title')),
                        'start': start_date.strftime('%Y-%m-%d %H:%M %Z'),
                        'description': str(component.get('description', 'No Description')),
                        'location': str(component.get('location', 'No Location'))
                    })
        
        # Sort events by start time
        events.sort(key=lambda x: x['start'])
        return events
    except Exception as e:
        print(f"Error parsing iCal data: {e}")
        return []

class CalendarRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Get parameters with defaults
        ical_url = query_params.get('url', ['http://192.168.1.146:8888/abfuhrtermine.ics'])[0]
        start_day = int(query_params.get('start', ['0'])[0])  # Default to today (0)
        end_day = int(query_params.get('end', ['2'])[0])      # Default to 2 days ahead
        plaintext = query_params.get('plaintext', ['false'])[0].lower() == 'true'

        # Validate parameters
        if start_day < 0:
            start_day = 0
        if end_day <= start_day:
            end_day = start_day + 1

        # Download and parse the calendar
        ical_data = download_ical(ical_url)
        
        if ical_data:
            events = parse_events(ical_data, start_day, end_day)
            
            if plaintext:
                # Send plaintext response
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Create plaintext response with one event summary per line
                response_text = '\n'.join(event['summary'] for event in events)
                if not response_text:
                    response_text = 'No events found.'
                self.wfile.write(response_text.encode('utf-8'))
            else:
                # Send JSON response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'status': 'success',
                    'events': events,
                    'count': len(events)
                }
                response_json = json.dumps(response_data, indent=2, ensure_ascii=False)
                self.wfile.write(response_json.encode('utf-8'))
        else:
            # Send error response in appropriate format
            self.send_response(200)
            if plaintext:
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                error_message = 'Failed to retrieve iCal data'
            else:
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                error_message = json.dumps({
                    'status': 'error',
                    'message': 'Failed to retrieve iCal data'
                }, ensure_ascii=False)
            
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(error_message.encode('utf-8'))

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CalendarRequestHandler)

    print(f"Server running on port {port}...")
    print(f"Try accessing: http://localhost:{port}?start=0&end=2")
    print(f"Parameters:")
    print(f"  - url: iCal URL (optional)")
    print(f"  - start: Start day offset from today (0 = today, 1 = tomorrow, etc.)")
    print(f"  - end: End day offset from today (must be greater than start)")
    print(f"  - plaintext: Set to 'true' for plain text output (optional)")
    print("\nPress Ctrl+C to shutdown the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("\nServer has been shut down.")

if __name__ == "__main__":
    run_server()
