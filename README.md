# Delhi Metro Route Finder 🚇

A modern, interactive web application for finding optimal routes in the Delhi Metro network. Built with Flask and vanilla JavaScript, featuring real-time pathfinding algorithms and an SVG-based metro map visualization.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-37%20passed-brightgreen.svg)

## ✨ Features

### Core Functionality
- **Optimized Pathfinding**: Heap-based Dijkstra's algorithm with O(n log n) complexity
- **Route Comparison**: Compare shortest distance vs. fewest line changes routes
- **Real-time Fare Calculation**: Token and Smart Card pricing with 10% discount
- **220+ Stations**: Comprehensive coverage of Delhi Metro network

### User Experience
- **Intelligent Search**: Autocomplete with keyboard navigation (Arrow keys + Enter)
- **Interactive Metro Map**: SVG-based visualization with line colors
- **Route Comparison Cards**: Side-by-side analysis of different routes
- **Mobile Responsive**: Works seamlessly on all device sizes

### Technical Excellence
- **Type-Annotated Code**: Full type hints for maintainability
- **Comprehensive Testing**: 37 unit tests covering edge cases
- **Rate Limiting**: Built-in request throttling for API stability
- **Logging**: Structured logging for debugging and monitoring

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| Backend | Python 3.10+, Flask 3.0 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Algorithm | Dijkstra's with Binary Heap |
| Visualization | Dynamic SVG Generation |
| Testing | Pytest |

## 📁 Project Structure

```
delhi_metro/
├── app.py                 # Flask application & API endpoints
├── metro_graph.py         # Graph data structure & algorithms
├── dmrc_api.py            # DMRC API integration (mock/live)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── static/
│   ├── script.js          # Frontend interactivity & visualization
│   └── style.css          # Modern responsive styling
├── templates/
│   └── index.html         # Main application template
└── tests/
    └── test_metro_graph.py # Unit tests
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/delhi-metro-route-finder.git
   cd delhi-metro-route-finder
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

## 🧪 Running Tests

```bash
# Run all tests with verbose output
pytest tests/test_metro_graph.py -v

# Run with coverage report
pytest tests/test_metro_graph.py --cov=metro_graph --cov-report=html
```

## 📊 Algorithm Details

### Dijkstra's Algorithm Implementation

The pathfinding uses an optimized heap-based implementation:

```python
def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float, List[Dict]]:
    """
    Finds shortest path using Dijkstra's algorithm with binary heap.
    
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)
    
    Args:
        start: Starting station name
        end: Destination station name
        
    Returns:
        Tuple of (path, total_distance, line_changes)
    """
```

### Route Types

| Route Type | Algorithm | Optimization |
|------------|-----------|--------------|
| Shortest | Dijkstra's | Minimize distance |
| Least Changes | Modified BFS | Minimize line transfers |
| Compare | Both | Side-by-side analysis |

## 🎨 Metro Lines

| Line | Color | Stations |
|------|-------|----------|
| Yellow | 🟡 #FFCC00 | 37 |
| Blue | 🔵 #0066CC | 50 |
| Red | 🔴 #FF0000 | 29 |
| Green | 🟢 #00CC00 | 21 |
| Violet | 🟣 #9900CC | 34 |
| Magenta | 🩷 #CC0066 | 25 |
| Pink | 🩷 #FF69B4 | 38 |
| Grey | ⚫ #999999 | 3 |

## 💰 Fare Structure (2024)

| Distance | Token Fare | Smart Card |
|----------|------------|------------|
| 0-2 km | ₹10 | ₹9 |
| 2-5 km | ₹20 | ₹18 |
| 5-12 km | ₹30 | ₹27 |
| 12-21 km | ₹40 | ₹36 |
| 21-32 km | ₹50 | ₹45 |
| 32+ km | ₹60 | ₹54 |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application |
| `/find_route` | POST | Find route between stations |
| `/api/search_stations` | GET | Search stations by query |
| `/api/popular_stations` | GET | Get popular stations list |
| `/api/station_info/<name>` | GET | Get station details |
| `/api/network_stats` | GET | Get network statistics |

### Example API Request

```bash
curl -X POST http://localhost:5000/find_route \
  -H "Content-Type: application/json" \
  -d '{"start": "Rajiv Chowk", "end": "Kashmere Gate", "route_type": "shortest"}'
```

### Response Format

```json
{
  "success": true,
  "routes": {
    "shortest": {
      "path": ["Rajiv Chowk", "New Delhi", "Chawri Bazar", ...],
      "distance": 4.2,
      "line_changes": [...],
      "route_type": "shortest"
    }
  },
  "summary": {
    "start": "Rajiv Chowk",
    "end": "Kashmere Gate",
    "stations_count": 5,
    "distance_km": 4.2,
    "estimated_time_min": 12,
    "fare": {
      "token_fare": 20,
      "smart_card_fare": 18,
      "savings": 2
    }
  }
}
```

## 🎯 Key Learnings & Skills Demonstrated

- **Data Structures**: Graph implementation with adjacency lists
- **Algorithms**: Dijkstra's shortest path with priority queue optimization
- **Web Development**: Full-stack Flask application with REST APIs
- **UI/UX Design**: Responsive CSS Grid, accessibility considerations
- **Testing**: Pytest with fixtures and edge case coverage
- **Code Quality**: Type hints, logging, error handling

## 🔮 Future Enhancements

- [ ] Real-time train tracking integration
- [ ] Accessibility features (screen reader support)
- [ ] Multi-language support (Hindi, English)
- [ ] Journey history and favorites
- [ ] Push notifications for delays

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Delhi Metro Rail Corporation for network data
- Flask community for excellent documentation
- Contributors and testers

---

**Built with ❤️ for Delhi Metro commuters**
