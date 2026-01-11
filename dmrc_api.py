import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DMRCApi:
    """Class to handle interactions with the DMRC API"""
    
    def __init__(self, metro_graph_instance=None):
        # API configuration
        self.api_key = os.getenv('DMRC_API_KEY')
        self.base_url = 'https://api.dmrc.co.in/v1'  # Example base URL
        self.metro_graph_instance = metro_graph_instance # Store the MetroGraph instance
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Cache for API responses to reduce API calls
        self.cache = {}
        self.cache_expiry = {}  # Store expiry timestamps for cache items
        self.cache_duration = 3600  # Cache duration in seconds (1 hour)
        
        # Print a message if using dummy key
        if self.api_key == 'dummy_api_key_for_testing':
            print("Using mock API mode with simulated responses")
    
    def _make_request(self, endpoint, method='GET', params=None, data=None):
        """Make a request to the DMRC API with error handling and caching"""
        # Create cache key based on endpoint and parameters
        cache_key = f"{endpoint}_{json.dumps(params) if params else ''}_{json.dumps(data) if data else ''}"
        
        # Check if response is in cache and not expired
        current_time = datetime.now().timestamp()
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > current_time:
            return self.cache[cache_key]
        
        # Check if we're using a dummy API key (for development/testing)
        if self.api_key == 'dummy_api_key_for_testing':
            print(f"Using mock data for endpoint: {endpoint}")
            return self._get_mock_response(endpoint, params, data)
        
        # Make the API request
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()  # Raise exception for HTTP errors
            result = response.json()
            
            # Cache the response
            self.cache[cache_key] = result
            self.cache_expiry[cache_key] = current_time + self.cache_duration
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            # Return None or raise exception based on your error handling strategy
            return None
    
    def get_all_stations(self):
        """Get a list of all stations in the Delhi Metro network"""
        try:
            response = self._make_request('stations')
            if response and 'data' in response:
                # Extract station names from the API response
                return sorted([station['name'] for station in response['data']])
            return []
        except Exception as e:
            print(f"Error fetching stations: {e}")
            return []
    
    def get_station_lines(self, station_name):
        """Get the lines that pass through a specific station"""
        try:
            response = self._make_request(f'stations/{station_name}/lines')
            if response and 'data' in response:
                return response['data']
            return []
        except Exception as e:
            print(f"Error fetching station lines: {e}")
            # Fallback to the provided MetroGraph instance
            if self.metro_graph_instance:
                return self.metro_graph_instance.station_lines.get(station_name, [])
            return [] # Return empty list if no instance provided
    
    def find_route(self, source, destination):
        """Find the best route between source and destination stations"""
        try:
            data = {
                'source': source,
                'destination': destination
            }
            response = self._make_request('routes/find', method='POST', data=data)
            
            if not response:
                print("No response received from route finding API")
                raise Exception("No response from route finding service")
                
            if 'data' not in response:
                print("Invalid response format from route finding API")
                raise Exception("Invalid response from route finding service")
            
            route_data = response['data']
            
            # Check if stations array exists and is not empty
            if 'stations' not in route_data or not route_data['stations']:
                print(f"No route found between {source} and {destination}")
                raise Exception(f"No route found between {source} and {destination}")
            
            # Extract path, distance, and line changes from the API response
            path = [station['name'] for station in route_data.get('stations', [])]
            distance = route_data.get('distance', 0)
            
            # Process line changes
            line_changes = []
            for change in route_data.get('line_changes', []):
                line_changes.append({
                    'station': change.get('station'),
                    'from_lines': change.get('from_lines', []),
                    'to_lines': change.get('to_lines', []),
                    'position': change.get('position', 0)
                })
            
            return path, distance, line_changes
        except Exception as e:
            print(f"Error finding route: {e}")
            return None, 0, []
    
    def calculate_fare(self, distance):
        """Calculate fare based on distance using the DMRC API"""
        try:
            params = {'distance': distance}
            response = self._make_request('fares/calculate', params=params)
            
            if response and 'data' in response:
                return response['data'].get('fare', 0)
            
            # Fallback to local calculation if API fails
            return self._calculate_fare_locally(distance)
        except Exception as e:
            print(f"Error calculating fare: {e}")
            return self._calculate_fare_locally(distance)
    
    def _calculate_fare_locally(self, distance):
        """Fallback method to calculate fare locally if the API is unavailable"""
        if distance <= 2:
            return 10
        elif distance <= 5:
            return 20
        elif distance <= 12:
            return 30
        elif distance <= 21:
            return 40
        elif distance <= 32:
            return 50
        else:
            return 60
    
    def get_train_schedule(self, station_name, line=None):
        """Get train schedule for a specific station and optionally filter by line"""
        try:
            params = {'line': line} if line else None
            response = self._make_request(f'stations/{station_name}/schedule', params=params)
            
            if response and 'data' in response:
                return response['data']
            return []
        except Exception as e:
            print(f"Error fetching train schedule: {e}")
            return []
    
    def get_service_alerts(self):
        """Get current service alerts and disruptions"""
        try:
            response = self._make_request('alerts')
            if response and 'data' in response:
                return response['data']
            return []
        except Exception as e:
            print(f"Error fetching service alerts: {e}")
            return []
            
    def _get_mock_response(self, endpoint, params=None, data=None):
        """Generate mock responses for development and testing"""
        # Use the stored MetroGraph instance if available
        if not self.metro_graph_instance:
            print("[WARN] MetroGraph instance not provided to DMRCApi for mock responses.")
            # Attempt to create a new one as a last resort, though this might re-introduce issues
            # if called during initial app setup. Ideally, it should always be provided.
            from metro_graph import MetroGraph
            self.metro_graph_instance = MetroGraph()

        metro_graph = self.metro_graph_instance # Use the stored instance

        # Mock station list
        if endpoint == 'stations':
            # Use all stations from MetroGraph for comprehensive station list
            all_stations = metro_graph.get_all_stations()

            # Convert to the format expected by the API
            return {
                'data': [{'name': station} for station in all_stations]
            }
        
        # Mock station lines
        elif endpoint.startswith('stations/') and endpoint.endswith('/lines'):
            station_name = endpoint.split('/')[1]
            # Use MetroGraph to get accurate line information for all stations
            lines = metro_graph.station_lines.get(station_name, [])
            return {'data': lines}

        # Mock route finding
        elif endpoint == 'routes/find':
            source = data.get('source') if data else None
            destination = data.get('destination') if data else None

            # Use the actual MetroGraph instance to find the route
            path, distance, line_changes = metro_graph.find_shortest_path(source, destination)
            
            if not path:
                return {'data': {'stations': [], 'distance': 0, 'line_changes': []}}
            
            # Convert path to the format expected by the API
            stations = [{'name': station} for station in path]
            
            # Return the actual route data
            return {
                'data': {
                    'stations': stations,
                    'distance': distance,
                    'line_changes': line_changes
                }
            }
        
        # Mock fare calculation
        elif endpoint == 'fares/calculate':
            distance = params.get('distance', 0)
            return {'data': {'fare': self._calculate_fare_locally(distance)}}
        
        # Mock train schedule
        elif endpoint.startswith('stations/') and endpoint.endswith('/schedule'):
            station_name = endpoint.split('/')[1]

            # Get the lines for this station from MetroGraph
            station_lines = metro_graph.station_lines.get(station_name, [])

            if not station_lines:
                return {'data': []}
            
            # Generate realistic schedules based on the actual lines at this station
            schedules = []
            current_hour = 10  # Start at 10 AM for mock data
            
            for line in station_lines:
                # For each line, add a few upcoming trains
                for i in range(2):  # 2 trains per line
                    minute = (i * 7) + (hash(line) % 10)  # Distribute minutes based on line name
                    
                    # Find a destination station on this line
                    destination = None
                    for dest, lines in metro_graph.station_lines.items():
                        if line in lines and dest != station_name:
                            destination = dest
                            break
                    
                    if not destination:
                        continue
                        
                    # Format time
                    departure_time = f"{current_hour}:{minute:02d} {'AM' if current_hour < 12 else 'PM'}"
                    
                    schedules.append({
                        'line': line,
                        'destination': destination,
                        'departure_time': departure_time
                    })
            
            return {'data': schedules}
        
        # Mock service alerts
        elif endpoint == 'alerts':
            return {
                'data': [
                    {
                        'line': 'Blue Line',
                        'type': 'Delay',
                        'message': 'Minor delays due to technical issue',
                        'timestamp': '2023-08-15T09:30:00Z'
                    },
                    {
                        'line': 'Magenta Line',
                        'type': 'Maintenance',
                        'message': 'Planned maintenance work on Sunday',
                        'timestamp': '2023-08-14T18:00:00Z'
                    }
                ]
            }
        
        # Default empty response
        return {'data': []}
