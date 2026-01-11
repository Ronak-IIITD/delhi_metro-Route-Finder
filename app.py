from flask import Flask, render_template, request, jsonify
from metro_graph import MetroGraph
from dmrc_api import DMRCApi
import os
import logging
from functools import wraps
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Rate limiting (simple in-memory implementation)
request_counts = {}
RATE_LIMIT = 60  # requests per minute

def rate_limit(f):
    """Simple rate limiting decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_minute = datetime.now().strftime('%Y-%m-%d-%H-%M')
        key = f"{client_ip}:{current_minute}"
        
        request_counts[key] = request_counts.get(key, 0) + 1
        
        if request_counts[key] > RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({
                'status': 'error',
                'message': 'Too many requests. Please try again later.'
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function

# Initialize the local MetroGraph first
metro_network = MetroGraph()

# Use DMRC API if API key is available, otherwise fallback to local data
if os.getenv('DMRC_API_KEY'):
    logger.info("Using DMRC API for real-time data")
    # Pass the metro_network instance to DMRCApi
    metro_service = DMRCApi(metro_graph_instance=metro_network)
else:
    logger.info("API key not found. Using local data.")
    # Use the already initialized MetroGraph instance
    metro_service = metro_network

@app.route('/')
def home():
    """Render the main page with station data."""
    stations = metro_service.get_all_stations()
    popular_stations = metro_network.get_popular_stations()
    interchange_stations = metro_network.get_interchange_stations()
    
    return render_template(
        'index.html', 
        stations=stations,
        popular_stations=popular_stations,
        interchange_stations=interchange_stations,
        last_updated=metro_network.last_updated.strftime('%B %Y')
    )

@app.route('/api/search_stations', methods=['GET'])
def search_stations():
    """Search stations by partial name match."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'stations': []})
    
    matches = metro_network.search_stations(query)
    return jsonify({'stations': matches})

@app.route('/api/popular_stations', methods=['GET'])
def get_popular_stations():
    """Get list of popular stations."""
    return jsonify({
        'popular': metro_network.get_popular_stations(),
        'interchanges': metro_network.get_interchange_stations()
    })

@app.route('/find_route', methods=['POST'])
@rate_limit
def find_route():
    """Find route between two stations with multiple optimization options."""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid request data'}), 400
    
    source = data.get('source', '').strip()
    destination = data.get('destination', '').strip()
    route_type = data.get('route_type', 'shortest')  # shortest, least_changes, or all
    use_smart_card = data.get('use_smart_card', False)
    
    # Validation
    if not source or not destination:
        return jsonify({
            'status': 'error', 
            'message': 'Please select both source and destination stations'
        }), 400
    
    # Check for same station
    if source.lower() == destination.lower():
        return jsonify({
            'status': 'error',
            'message': 'Source and destination cannot be the same station'
        }), 400
    
    # Check if stations exist in the network
    all_stations = metro_service.get_all_stations()
    all_stations_lower = {s.lower(): s for s in all_stations}
    
    if source.lower() not in all_stations_lower:
        return jsonify({
            'status': 'error', 
            'message': f'Station "{source}" not found. Please check the spelling.'
        }), 404
    
    if destination.lower() not in all_stations_lower:
        return jsonify({
            'status': 'error', 
            'message': f'Station "{destination}" not found. Please check the spelling.'
        }), 404
    
    # Normalize station names
    source = all_stations_lower[source.lower()]
    destination = all_stations_lower[destination.lower()]
    
    try:
        # Find routes based on requested type
        if route_type == 'all':
            routes = metro_network.find_all_routes(source, destination)
            if not routes:
                return jsonify({
                    'status': 'error',
                    'message': f'No route found between {source} and {destination}.'
                }), 404
            
            # Format all routes for response
            formatted_routes = []
            for route in routes:
                fare_info = metro_network.calculate_fare(route.distance, use_smart_card)
                station_lines = _get_station_lines(route.path)
                summary = metro_network.get_route_summary(route.path, route.distance, route.line_changes)
                
                formatted_routes.append({
                    'route_type': route.route_type,
                    'path': route.path,
                    'distance': route.distance,
                    'stations_count': len(route.path),
                    'station_lines': station_lines,
                    'line_changes': route.line_changes,
                    'fare': fare_info,
                    'estimated_time': summary['estimated_time_min']
                })
            
            return jsonify({
                'status': 'success',
                'routes': formatted_routes,
                'selected_route': formatted_routes[0]  # Default to first route
            })
        
        else:
            # Single route request
            if route_type == 'least_changes':
                path, distance, line_changes = metro_network.find_route_least_changes(source, destination)
            else:
                path, distance, line_changes = metro_network.find_shortest_path(source, destination)
            
            if not path:
                return jsonify({
                    'status': 'error',
                    'message': f'No route found between {source} and {destination}.'
                }), 404
            
            # Calculate fare
            fare_info = metro_network.calculate_fare(distance, use_smart_card)
            
            # Get station line information
            station_lines = _get_station_lines(path)
            
            # Get route summary
            summary = metro_network.get_route_summary(path, distance, line_changes)
            
            return jsonify({
                'status': 'success',
                'path': path,
                'distance': distance,
                'stations_count': len(path),
                'station_lines': station_lines,
                'line_changes': line_changes,
                'fare': fare_info,
                'estimated_time': summary['estimated_time_min'],
                'route_type': route_type
            })
            
    except Exception as e:
        logger.exception(f"Error finding route from {source} to {destination}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again.'
        }), 500


def _get_station_lines(path):
    """Helper function to get line information for each station in path."""
    station_lines = []
    for station in path:
        lines = metro_network.station_lines.get(station, [])
        station_lines.append({
            'station': station,
            'lines': lines
        })
    return station_lines


@app.route('/api/station_info/<station_name>', methods=['GET'])
def get_station_info(station_name):
    """Get detailed information about a specific station."""
    stations = metro_network.get_all_stations()
    stations_lower = {s.lower(): s for s in stations}
    
    if station_name.lower() not in stations_lower:
        return jsonify({'status': 'error', 'message': 'Station not found'}), 404
    
    actual_name = stations_lower[station_name.lower()]
    lines = metro_network.station_lines.get(actual_name, [])
    is_interchange = len(lines) > 1
    
    # Get connected stations
    connected = list(metro_network.graph.get(actual_name, {}).keys())
    
    return jsonify({
        'status': 'success',
        'station': {
            'name': actual_name,
            'lines': lines,
            'is_interchange': is_interchange,
            'connected_stations': connected
        }
    })


@app.route('/api/network_stats', methods=['GET'])
def get_network_stats():
    """Get statistics about the metro network."""
    total_stations = len(metro_network.stations)
    total_lines = len(metro_network.lines)
    interchange_count = len(metro_network.get_interchange_stations())
    
    # Calculate total track length (approximate)
    total_distance = 0
    counted_edges = set()
    for station, neighbors in metro_network.graph.items():
        for neighbor, distance in neighbors.items():
            edge = tuple(sorted([station, neighbor]))
            if edge not in counted_edges:
                total_distance += distance
                counted_edges.add(edge)
    
    return jsonify({
        'status': 'success',
        'stats': {
            'total_stations': total_stations,
            'total_lines': total_lines,
            'interchange_stations': interchange_count,
            'total_track_km': round(total_distance, 2),
            'last_updated': metro_network.last_updated.strftime('%Y-%m-%d')
        }
    })


if __name__ == '__main__':
    # Use environment variable for debug mode in production
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
