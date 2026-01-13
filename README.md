# Delhi Metro Route Finder 🚇

> A web app to find the best routes in the Delhi Metro network, built with Flask and Python

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## What is this?

Ever struggled to figure out the fastest metro route in Delhi? This web app helps you find the best path between any two metro stations. It calculates:
- **Shortest distance route** - Gets you there using the least kilometers
- **Least line changes** - Minimizes the number of times you switch lines
- **Fare calculation** - Shows both token and smart card prices
- **Travel time estimates** - Tells you roughly how long it'll take

I built this as a learning project to understand graph algorithms and full-stack web development.


**Live features:**
- Search 220+ Delhi Metro stations
- Interactive route visualization
- Compare different route options
- Real-time fare calculation
- Works on mobile and desktop

## Why I Built This

As a sophomore at IIIT Delhi, I wanted to:
1. Learn how pathfinding algorithms actually work (not just in theory!)
2. Build something practical that people can use
3. Get hands-on with Flask and web development
4. Understand graph data structures better

Plus, I take the metro often and thought it would be cool to build this myself instead of using Google Maps all the time!

## Tech Stack

| Component | Technology | Why I chose it |
|-----------|-----------|----------------|
| Backend | Python 3.10 + Flask | Easy to learn, great for APIs |
| Algorithm | Dijkstra's (with heap) | Best for shortest path problems |
| Frontend | HTML/CSS/JavaScript | Keeps it simple, no frameworks needed |
| Data Structure | Adjacency List Graph | Efficient for metro networks |
| Testing | Pytest | Industry standard for Python |

## Project Structure

```
delhi-metro-route-finder/
├── app.py              # Flask backend (API routes, server)
├── metro_graph.py      # Core algorithm (Dijkstra's implementation)
├── dmrc_api.py         # API wrapper (currently uses local data)
├── static/
│   ├── script.js       # Frontend logic
│   └── style.css       # UI styling
├── templates/
│   └── index.html      # Main webpage
├── tests/
│   └── test_metro_graph.py  # Unit tests
└── requirements.txt    # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.10 or higher ([Download here](https://www.python.org/downloads/))
- pip (comes with Python)
- A terminal/command prompt

### Quick Setup (Recommended)

**Option 1: Automatic Setup (Linux/Mac)**
```bash
# Clone the repository
git clone https://github.com/Ronak-IIITD/delhi_metro-Route-Finder.git
cd delhi-metro-route-finder

# Run the setup script (does everything for you!)
bash setup.sh
```

**Option 2: Manual Setup (All platforms)**

```bash
# 1. Clone the repository
git clone https://github.com/Ronak-IIITD/delhi_metro-Route-Finder.git
cd delhi-metro-route-finder

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment variables
cp .env.example .env

# 6. Run the app
python app.py
```

### Running the App

Once setup is complete:
```bash
python app.py
```

Then open your browser and go to: **http://localhost:5000**

That's it! 🎉

## How It Works

### The Algorithm

I implemented Dijkstra's shortest path algorithm with a binary heap (priority queue) for optimal performance:

```python
# Simplified version of what happens:
def find_shortest_path(start, end):
    distances = {station: infinity for all stations}
    distances[start] = 0
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_station = pop_min(priority_queue)
        
        if current_station == end:
            return reconstruct_path()
        
        for neighbor in current_station.neighbors:
            new_distance = current_distance + edge_weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                push(priority_queue, (new_distance, neighbor))
```

**Time Complexity:** O((V + E) log V) where V = stations, E = connections  
**Space Complexity:** O(V)

### Data Structure

The metro network is represented as a **weighted graph** using an adjacency list:
- **Nodes** = Metro stations
- **Edges** = Direct connections between stations
- **Weights** = Distance in kilometers

Example:
```python
graph = {
    "Rajiv Chowk": {
        "Patel Chowk": 1.3,      # 1.3 km away
        "Barakhamba Road": 0.7,  # 0.7 km away
    },
    ...
}
```

## Features in Detail

### 1. Route Finding
- **Shortest Distance:** Finds the path with minimum total kilometers
- **Least Changes:** Minimizes line switching (useful when carrying luggage!)
- **Compare Mode:** Shows both routes side by side

### 2. Fare Calculator
Based on official DMRC fare structure (2024):
- Up to 2 km → ₹10
- 2-5 km → ₹20
- 5-12 km → ₹30
- 12-21 km → ₹40
- 21-32 km → ₹50
- Above 32 km → ₹60

*Smart card users get 10% off!*

### 3. Station Search
- Autocomplete with 220+ stations
- Fuzzy matching (works even with typos)
- Keyboard navigation (arrow keys + enter)

### 4. Network Coverage
- **8 metro lines** (Yellow, Blue, Red, Green, Violet, Magenta, Pink, Grey)
- **220+ stations**
- **Latest network** (updated January 2026)

## What I Learned

### Technical Skills
- **Data Structures:** How to implement and use graphs effectively
- **Algorithms:** Understanding Dijkstra's algorithm beyond just theory
- **Web Development:** Building REST APIs with Flask
- **Frontend:** Making responsive UIs with vanilla JavaScript
- **Testing:** Writing meaningful unit tests with pytest

### Challenges I Faced

1. **Getting Dijkstra's right:** Initially used a basic queue which was slow (O(V²)). Learned about heaps and optimized it to O((V+E) log V).

2. **Handling line changes:** Figuring out when users switch metro lines was trickier than expected. Had to track which line you're on at each station.

3. **Station name matching:** Users type station names differently (e.g., "Rajiv Chowk" vs "rajiv chowk"). Implemented case-insensitive fuzzy search.

4. **Test coverage:** Writing tests for edge cases (same source/destination, invalid stations, disconnected routes) taught me to think like a user.

## Testing

Run the test suite:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=metro_graph --cov-report=html
```

Current test coverage: **37 tests, all passing** ✅

Tests include:
- Route finding accuracy
- Fare calculation
- Edge cases (invalid input, same station, etc.)
- Performance benchmarks

## API Documentation

The backend exposes several REST endpoints:

### Find Route
```http
POST /find_route
Content-Type: application/json

{
    "source": "Rajiv Chowk",
    "destination": "Kashmere Gate",
    "route_type": "shortest"  // or "least_changes" or "all"
}
```

### Search Stations
```http
GET /api/search_stations?q=rajiv
```

### Station Info
```http
GET /api/station_info/Rajiv Chowk
```

See [app.py](app.py) for complete API documentation.

## Future Improvements

Things I want to add next:
- [ ] Real-time train tracking (if DMRC API becomes available)
- [ ] Save favorite routes
- [ ] Journey history
- [ ] Offline mode with PWA
- [ ] Accessibility improvements (screen reader support)
- [ ] Hindi language support
- [ ] Share route via link

## Contributing

This is a learning project, but I'm open to suggestions! If you find a bug or have an idea:
1. Open an issue
2. Fork the repo and make your changes
3. Submit a pull request

Please be kind - I'm still learning!

## Project Stats

- **Lines of Code:** ~1,500 (Python + JavaScript)
- **Development Time:** ~2 weeks
- **Stations Covered:** 220+
- **Test Coverage:** 37 tests
- **Coffee Consumed:** Too much ☕

## Acknowledgments

- Delhi Metro Rail Corporation (DMRC) for the network data
- My DSA professor for teaching graph algorithms
- Stack Overflow for helping me debug at 2 AM
- My friends who tested the app and found bugs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by Ronak Anand**  
Sophomore @ IIIT Delhi

*If you found this helpful, give it a star! ⭐*

---

### Connect with me
- GitHub: [@Ronak-IIITD](https://github.com/Ronak-IIITD)
- Project Link: [https://github.com/Ronak-IIITD/delhi_metro-Route-Finder](https://github.com/Ronak-IIITD/delhi_metro-Route-Finder)

### Questions?

Feel free to open an issue or reach out if you have questions about the code or want to discuss the project!
