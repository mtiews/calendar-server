# Calendar Event Filter

A lightweight Python-based web server that fetches and filters iCal calendar events loaded from another (configurable) URL. It provides both JSON and plain text outputs for events filtered within a specified date range.

This is a small support project for my ESP32-S3 based e-Paper displays where I'm using ESPHome to program them, and for processing and parsing iCal I didn't find an easy way. 

## Features

- Fetch events from any iCal URL
- Filter events by date range using day offsets (0 = today, 1 = tomorrow, etc.)
- Support for both JSON and plain text output formats
- Proper UTC timezone handling
- CORS enabled for cross-origin requests
- Docker support for easy deployment

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository and cd into it.
2. Create and activate Virtual Environment:
   ```powershell
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Server

#### Direct Python Execution

Run the server directly with Python:
```powershell
python src/calendar_filter.py
```

The server will start on port 8080 by default.

#### Using Docker

1. Build the Docker image:
   ```powershell
   docker build -t calendar-server .
   ```

2. Run the container:
   ```powershell
   docker run -p 8080:8080 calendar-server
   ```

## API Usage

The server provides a simple HTTP API for fetching calendar events.

### Endpoints

`GET /`

### Query Parameters

| Parameter  | Description | Default | Example |
|------------|-------------|---------|---------|
| url        | iCal URL to fetch from | http://192.168.1.146:8888/abfuhrtermine.ics | `?url=https://example.com/calendar.ics` |
| start      | Start day offset from today | 0 | `?start=0` (today) |
| end        | End day offset from today | 2 | `?end=7` (a week ahead) |
| plaintext  | Return plain text instead of JSON | false | `?plaintext=true` |

### Response Formats

#### JSON Format (default)
```json
{
  "status": "success",
  "events": [
    {
      "summary": "Event Title",
      "start": "2025-10-22 14:00 UTC",
      "description": "Event Description",
      "location": "Event Location"
    }
  ],
  "count": 1
}
```

#### Plain Text Format
When `plaintext=true`, returns one event summary per line:
```
Event 1 Title
Event 2 Title
Event 3 Title
```

### Example Requests

1. Get events for today and tomorrow (JSON):
   ```
   http://localhost:8080?start=0&end=2
   ```

2. Get events for next week in plain text:
   ```
   http://localhost:8080?start=7&end=14&plaintext=true
   ```

3. Get events from a specific calendar:
   ```
   http://localhost:8080?url=https://example.com/calendar.ics&start=0&end=7
   ```

## Development

### Project Structure

```
Calendar/
├── src/
│   └── calendar_filter.py    # Main application code
├── Dockerfile               # Docker configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Dependencies

- requests: For fetching iCal files
- icalendar: For parsing iCal data
- pytz: For timezone handling

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Error Handling

The server handles various error cases:

- Invalid iCal URL: Returns error message
- Invalid date parameters: Adjusts to valid ranges
- Missing timezone information: Assumes UTC
- Parse errors: Returns appropriate error message

## Security Considerations

- The server includes CORS headers for cross-origin requests
- URLs are validated before fetching
- Error messages are sanitized
- Running in Docker provides container isolation

## License

[Add your license information here]

## Contributing

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request