import heapq
import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Data class for route finding results"""

    path: List[str]
    distance: float
    line_changes: List[dict]
    route_type: str = "shortest"  # shortest, least_changes, direct


class MetroGraph:
    """
    Delhi Metro Network Graph Implementation

    Uses an adjacency list representation with Dijkstra's algorithm (heap-optimized)
    for finding shortest paths. Supports multiple route finding strategies.

    Data Source: Delhi Metro Rail Corporation (DMRC) - Updated January 2026
    """

    # Popular stations for quick access
    POPULAR_STATIONS = [
        "Rajiv Chowk",
        "New Delhi",
        "Kashmere Gate",
        "Central Secretariat",
        "Hauz Khas",
        "Huda City Centre",
        "AIIMS",
        "INA",
        "Dwarka Sector 21",
        "Noida City Centre",
        "Botanical Garden",
        "Mandi House",
        "Lajpat Nagar",
    ]

    def __init__(self):
        # Initialize the graph as an adjacency list
        self.graph: Dict[str, Dict[str, float]] = {}
        self.stations: Set[str] = set()
        self.station_lines: Dict[str, List[str]] = {}  # Map stations to their lines
        self.lines: Dict[str, List[str]] = {}  # Store line information
        self.last_updated = datetime(2026, 1, 11)  # Data last verified date

        # Initialize with Delhi Metro stations and connections
        self._initialize_metro_network()
        logger.info(f"MetroGraph initialized with {len(self.stations)} stations")

    def _initialize_metro_network(self) -> None:
        """
        Initialize the Delhi Metro network with stations and connections.
        Each connection has a distance (in km) between stations.

        Data Source: Delhi Metro Rail Corporation (DMRC)
        Last Updated: January 2026

        Note: Distances are based on official DMRC data where available,
        with estimates for newer sections pending official confirmation.
        """
        # Define metro lines with their stations
        # Format: [(station1, station2, distance), ...]

        # Yellow Line (Line 2) - Samaypur Badli to Huda City Centre
        yellow_line = [
            ("Samaypur Badli", "Rohini Sector 18,19", 1.3),
            ("Rohini Sector 18,19", "Haiderpur Badli Mor", 1.2),
            ("Haiderpur Badli Mor", "Jahangirpuri", 1.4),
            ("Jahangirpuri", "Adarsh Nagar", 1.3),
            ("Adarsh Nagar", "Azadpur", 1.5),
            ("Azadpur", "Model Town", 1.4),
            ("Model Town", "GTB Nagar", 1.4),
            ("GTB Nagar", "Vishwa Vidyalaya", 0.8),
            ("Vishwa Vidyalaya", "Vidhan Sabha", 1.0),
            ("Vidhan Sabha", "Civil Lines", 1.3),
            ("Civil Lines", "Kashmere Gate", 1.1),
            ("Kashmere Gate", "Chandni Chowk", 1.1),
            ("Chandni Chowk", "Chawri Bazar", 1.0),
            ("Chawri Bazar", "New Delhi", 0.8),
            ("New Delhi", "Rajiv Chowk", 1.1),
            ("Rajiv Chowk", "Patel Chowk", 1.3),
            ("Patel Chowk", "Central Secretariat", 0.9),
            ("Central Secretariat", "Udyog Bhawan", 0.3),
            ("Udyog Bhawan", "Lok Kalyan Marg", 1.6),
            ("Lok Kalyan Marg", "Jor Bagh", 1.2),
            ("Jor Bagh", "INA", 1.3),
            ("INA", "AIIMS", 0.8),
            ("AIIMS", "Green Park", 1.0),
            ("Green Park", "Hauz Khas", 1.8),
            ("Hauz Khas", "Malviya Nagar", 1.7),
            ("Malviya Nagar", "Saket", 0.9),
            ("Saket", "Qutab Minar", 1.7),
            ("Qutab Minar", "Chhatarpur", 1.5),
            ("Chhatarpur", "Sultanpur", 1.5),
            ("Sultanpur", "Ghitorni", 1.3),
            ("Ghitorni", "Arjan Garh", 2.7),
            ("Arjan Garh", "Guru Dronacharya", 2.3),
            ("Guru Dronacharya", "Sikanderpur", 1.0),
            ("Sikanderpur", "MG Road", 1.2),
            ("MG Road", "IFFCO Chowk", 1.1),
            ("IFFCO Chowk", "Huda City Centre", 1.5),
        ]

        # Blue Line (Updated with extension)
        blue_line = [
            ("Dwarka Sector 21", "Dwarka Sector 8", 2.6),
            ("Dwarka Sector 8", "Dwarka Sector 9", 1.7),
            ("Dwarka Sector 9", "Dwarka Sector 10", 1.0),
            ("Dwarka Sector 10", "Dwarka Sector 11", 1.2),
            ("Dwarka Sector 11", "Dwarka Sector 12", 1.0),
            ("Dwarka Sector 12", "Dwarka Sector 13", 1.1),
            ("Dwarka Sector 13", "Dwarka Sector 14", 1.1),
            ("Dwarka Sector 14", "Dwarka", 1.0),
            ("Dwarka", "Dwarka Mor", 1.2),
            ("Dwarka Mor", "Nawada", 1.7),
            ("Nawada", "Uttam Nagar West", 1.0),
            ("Uttam Nagar West", "Uttam Nagar East", 0.9),
            ("Uttam Nagar East", "Janakpuri West", 1.0),
            ("Janakpuri West", "Janakpuri East", 1.1),
            ("Janakpuri East", "Tilak Nagar", 1.1),
            ("Tilak Nagar", "Subhash Nagar", 1.3),
            ("Subhash Nagar", "Tagore Garden", 1.0),
            ("Tagore Garden", "Rajouri Garden", 1.2),
            ("Rajouri Garden", "Ramesh Nagar", 1.2),
            ("Ramesh Nagar", "Moti Nagar", 1.2),
            ("Moti Nagar", "Kirti Nagar", 1.1),
            ("Kirti Nagar", "Shadipur", 0.7),
            ("Shadipur", "Patel Nagar", 1.3),
            ("Patel Nagar", "Rajendra Place", 1.1),
            ("Rajendra Place", "Karol Bagh", 1.1),
            ("Karol Bagh", "Jhandewalan", 1.2),
            ("Jhandewalan", "Ramakrishna Ashram Marg", 0.8),
            ("Ramakrishna Ashram Marg", "Rajiv Chowk", 1.1),
            ("Rajiv Chowk", "Barakhamba Road", 0.7),
            ("Barakhamba Road", "Mandi House", 1.0),
            ("Mandi House", "Supreme Court", 0.9),
            ("Supreme Court", "Indraprastha", 1.1),
            ("Indraprastha", "Yamuna Bank", 1.8),
            ("Yamuna Bank", "Akshardham", 1.3),
            ("Akshardham", "Mayur Vihar Phase 1", 1.8),
            ("Mayur Vihar Phase 1", "Mayur Vihar Extension", 1.2),
            ("Mayur Vihar Extension", "New Ashok Nagar", 1.0),
            ("New Ashok Nagar", "Noida Sector 15", 1.7),
            ("Noida Sector 15", "Noida Sector 16", 1.1),
            ("Noida Sector 16", "Noida Sector 18", 1.5),
            ("Noida Sector 18", "Botanical Garden", 1.6),
            ("Botanical Garden", "Golf Course", 1.2),
            ("Golf Course", "Noida City Centre", 1.3),
            ("Noida City Centre", "Noida Sector 62", 1.6),
            ("Noida Sector 62", "Noida Electronic City", 1.5),
        ]

        # Blue Line Branch (Yamuna Bank to Vaishali)
        blue_line_branch = [
            ("Yamuna Bank", "Laxmi Nagar", 1.3),
            ("Laxmi Nagar", "Nirman Vihar", 1.1),
            ("Nirman Vihar", "Preet Vihar", 1.0),
            ("Preet Vihar", "Karkardooma", 1.2),
            ("Karkardooma", "Anand Vihar ISBT", 1.1),
            ("Anand Vihar ISBT", "Kaushambi", 0.8),
            ("Kaushambi", "Vaishali", 1.6),
        ]

        # Red Line (Updated)
        red_line = [
            ("Rithala", "Rohini West", 1.5),
            ("Rohini West", "Rohini East", 1.2),
            ("Rohini East", "Pitampura", 1.1),
            ("Pitampura", "Kohat Enclave", 1.1),
            ("Kohat Enclave", "Netaji Subhash Place", 0.9),
            ("Netaji Subhash Place", "Keshav Puram", 1.2),
            ("Keshav Puram", "Kanhaiya Nagar", 0.8),
            ("Kanhaiya Nagar", "Inderlok", 1.2),
            ("Inderlok", "Shastri Nagar", 1.2),
            ("Shastri Nagar", "Pratap Nagar", 1.7),
            ("Pratap Nagar", "Pulbangash", 0.8),
            ("Pulbangash", "Tis Hazari", 0.9),
            ("Tis Hazari", "Kashmere Gate", 1.1),
            ("Kashmere Gate", "Shastri Park", 2.2),
            ("Shastri Park", "Seelampur", 1.6),
            ("Seelampur", "Welcome", 1.1),
            ("Welcome", "Shahdara", 1.3),
            ("Shahdara", "Mansarovar Park", 1.1),
            ("Mansarovar Park", "Jhilmil", 1.1),
            ("Jhilmil", "Dilshad Garden", 1.3),
            ("Dilshad Garden", "Shaheed Nagar", 1.1),
            ("Shaheed Nagar", "Raj Bagh", 1.2),
            ("Raj Bagh", "Rajendra Nagar", 1.1),
            ("Rajendra Nagar", "Shyam Park", 1.0),
            ("Shyam Park", "Mohan Nagar", 1.3),
            ("Mohan Nagar", "Arthala", 1.0),
            ("Arthala", "Hindon River", 0.9),
            ("Hindon River", "Shaheed Sthal", 1.4),
        ]

        # Green Line (Updated with extension)
        green_line = [
            ("Inderlok", "Ashok Park Main", 1.4),
            ("Ashok Park Main", "Punjabi Bagh", 1.3),
            ("Punjabi Bagh", "Shivaji Park", 1.6),
            ("Shivaji Park", "Madipur", 1.1),
            ("Madipur", "Paschim Vihar East", 1.2),
            ("Paschim Vihar East", "Paschim Vihar West", 1.0),
            ("Paschim Vihar West", "Peera Garhi", 1.7),
            ("Peera Garhi", "Udyog Nagar", 0.8),
            ("Udyog Nagar", "Surajmal Stadium", 1.2),
            ("Surajmal Stadium", "Nangloi", 1.1),
            ("Nangloi", "Nangloi Railway Station", 0.9),
            ("Nangloi Railway Station", "Rajdhani Park", 1.1),
            ("Rajdhani Park", "Mundka", 1.4),
            ("Mundka", "Mundka Industrial Area", 1.2),
            ("Mundka Industrial Area", "Ghevra", 1.3),
            ("Ghevra", "Tikri Kalan", 1.1),
            ("Tikri Kalan", "Tikri Border", 1.0),
            ("Tikri Border", "Pandit Shree Ram Sharma", 1.2),
            ("Pandit Shree Ram Sharma", "Bahadurgarh City", 1.3),
            ("Bahadurgarh City", "Brigadier Hoshiar Singh", 1.5),
        ]

        # Green Line Branch (Ashok Park Main to Kirti Nagar)
        green_line_branch = [
            ("Ashok Park Main", "Satguru Ram Singh Marg", 1.1),
            ("Satguru Ram Singh Marg", "Kirti Nagar", 1.0),
        ]

        # Violet Line (Updated)
        violet_line = [
            ("Kashmere Gate", "Lal Quila", 1.5),
            ("Lal Quila", "Jama Masjid", 0.8),
            ("Jama Masjid", "Delhi Gate", 1.4),
            ("Delhi Gate", "ITO", 1.3),
            ("ITO", "Mandi House", 0.8),
            ("Mandi House", "Janpath", 1.0),
            ("Janpath", "Central Secretariat", 1.1),
            ("Central Secretariat", "Khan Market", 2.1),
            ("Khan Market", "JLN Stadium", 1.4),
            ("JLN Stadium", "Jangpura", 0.9),
            ("Jangpura", "Lajpat Nagar", 1.5),
            ("Lajpat Nagar", "Moolchand", 1.0),
            ("Moolchand", "Kailash Colony", 1.3),
            ("Kailash Colony", "Nehru Place", 1.0),
            ("Nehru Place", "Kalkaji Mandir", 1.2),
            ("Kalkaji Mandir", "Govind Puri", 0.9),
            ("Govind Puri", "Harkesh Nagar", 1.2),
            ("Harkesh Nagar", "Jasola Apollo", 0.9),
            ("Jasola Apollo", "Sarita Vihar", 1.5),
            ("Sarita Vihar", "Mohan Estate", 1.4),
            ("Mohan Estate", "Tughlakabad", 1.3),
            ("Tughlakabad", "Badarpur", 1.7),
            ("Badarpur", "Sarai", 1.9),
            ("Sarai", "NHPC Chowk", 1.3),  # Added missing connection
            ("NHPC Chowk", "Mewala Maharajpur", 1.2),
            ("Mewala Maharajpur", "Sector 28", 1.1),
            ("Sector 28", "Badkal Mor", 1.6),
            ("Badkal Mor", "Faridabad Old", 1.7),
            ("Faridabad Old", "Neelam Chowk Ajronda", 1.4),
            ("Neelam Chowk Ajronda", "Bata Chowk", 1.4),
            ("Bata Chowk", "Escorts Mujesar", 1.6),
            ("Escorts Mujesar", "Raja Nahar Singh", 1.5),
        ]

        # Magenta Line (New)
        magenta_line = [
            ("Janakpuri West", "Dabri Mor", 1.2),
            ("Dabri Mor", "Dashrath Puri", 1.1),
            ("Dashrath Puri", "Palam", 1.3),
            ("Palam", "Sadar Bazaar Cantonment", 1.4),
            ("Sadar Bazaar Cantonment", "Terminal 1 IGI Airport", 1.7),
            ("Terminal 1 IGI Airport", "Shankar Vihar", 1.5),
            ("Shankar Vihar", "Vasant Vihar", 1.3),
            ("Vasant Vihar", "Munirka", 1.0),
            ("Munirka", "R.K Puram", 1.2),
            ("R.K Puram", "IIT Delhi", 1.1),
            ("IIT Delhi", "Hauz Khas", 1.0),
            ("Hauz Khas", "Panchsheel Park", 1.3),
            ("Panchsheel Park", "Chirag Delhi", 1.2),
            ("Chirag Delhi", "Greater Kailash", 1.1),
            ("Greater Kailash", "Nehru Enclave", 1.0),
            ("Nehru Enclave", "Kalkaji Mandir", 1.2),
            ("Kalkaji Mandir", "Okhla NSIC", 1.3),
            ("Okhla NSIC", "Sukhdev Vihar", 1.0),
            ("Sukhdev Vihar", "Jamia Millia Islamia", 1.1),
            ("Jamia Millia Islamia", "Okhla Vihar", 1.2),
            ("Okhla Vihar", "Jasola Vihar Shaheen Bagh", 1.0),
            ("Jasola Vihar Shaheen Bagh", "Kalindi Kunj", 1.4),
            ("Kalindi Kunj", "Okhla Bird Sanctuary", 1.2),
            ("Okhla Bird Sanctuary", "Botanical Garden", 1.3),
        ]

        # Pink Line (New)
        pink_line = [
            ("Majlis Park", "Azadpur", 1.5),
            ("Azadpur", "Shalimar Bagh", 1.2),
            ("Shalimar Bagh", "Netaji Subhash Place", 1.3),
            ("Netaji Subhash Place", "Shakurpur", 1.1),
            ("Shakurpur", "Punjabi Bagh West", 1.4),
            ("Punjabi Bagh West", "ESI Hospital", 1.2),
            ("ESI Hospital", "Rajouri Garden", 1.1),
            ("Rajouri Garden", "Maya Puri", 1.5),
            ("Maya Puri", "Naraina Vihar", 1.0),
            ("Naraina Vihar", "Delhi Cantt", 1.3),
            ("Delhi Cantt", "Durgabai Deshmukh South Campus", 1.4),
            ("Durgabai Deshmukh South Campus", "Sir Vishweshwaraiah Moti Bagh", 1.2),
            ("Sir Vishweshwaraiah Moti Bagh", "Bhikaji Cama Place", 1.1),
            ("Bhikaji Cama Place", "Sarojini Nagar", 1.0),
            ("Sarojini Nagar", "INA", 1.3),
            ("INA", "South Extension", 1.2),
            ("South Extension", "Lajpat Nagar", 1.1),
            ("Lajpat Nagar", "Vinobapuri", 1.0),
            ("Vinobapuri", "Ashram", 1.2),
            ("Ashram", "Hazrat Nizamuddin", 1.3),
            ("Hazrat Nizamuddin", "Mayur Vihar Phase 1", 1.8),
            ("Mayur Vihar Phase 1", "Mayur Vihar Pocket 1", 1.0),
            ("Mayur Vihar Pocket 1", "Trilokpuri Sanjay Lake", 1.2),
            ("Trilokpuri Sanjay Lake", "East Vinod Nagar", 1.1),
            ("East Vinod Nagar", "IP Extension", 1.0),
            ("IP Extension", "Anand Vihar ISBT", 1.3),
            ("Anand Vihar ISBT", "Karkardooma", 1.2),
            ("Karkardooma", "Karkardooma Court", 1.1),
            ("Karkardooma Court", "Krishna Nagar", 1.0),
            ("Krishna Nagar", "East Azad Nagar", 1.1),
            ("East Azad Nagar", "Welcome", 1.2),
            ("Welcome", "Jaffrabad", 1.0),
            ("Jaffrabad", "Maujpur", 1.1),
            ("Maujpur", "Gokulpuri", 1.2),
            ("Gokulpuri", "Johri Enclave", 1.1),
            ("Johri Enclave", "Shiv Vihar", 1.3),
        ]

        # Grey Line (New)
        grey_line = [
            ("Dwarka", "Nangli", 1.3),
            ("Nangli", "Najafgarh", 1.2),
            ("Najafgarh", "Dhansa Bus Stand", 1.1),
        ]

        # Add all metro lines to the graph
        all_lines = (
            yellow_line
            + blue_line
            + blue_line_branch
            + red_line
            + green_line
            + green_line_branch
            + violet_line
            + magenta_line
            + pink_line
            + grey_line
        )  # Removed direct_connections

        # Store line information
        self.lines = {
            "Yellow": [
                station
                for station1, station2, _ in yellow_line
                for station in [station1, station2]
            ],
            "Blue": [
                station
                for station1, station2, _ in blue_line
                for station in [station1, station2]
            ],
            "Blue Branch": [
                station
                for station1, station2, _ in blue_line_branch
                for station in [station1, station2]
            ],
            "Red": [
                station
                for station1, station2, _ in red_line
                for station in [station1, station2]
            ],
            "Green": [
                station
                for station1, station2, _ in green_line
                for station in [station1, station2]
            ],
            "Green Branch": [
                station
                for station1, station2, _ in green_line_branch
                for station in [station1, station2]
            ],
            "Violet": [
                station
                for station1, station2, _ in violet_line
                for station in [station1, station2]
            ],
            "Magenta": [
                station
                for station1, station2, _ in magenta_line
                for station in [station1, station2]
            ],
            "Pink": [
                station
                for station1, station2, _ in pink_line
                for station in [station1, station2]
            ],
            "Grey": [
                station
                for station1, station2, _ in grey_line
                for station in [station1, station2]
            ],
        }

        # Build the graph
        for station1, station2, distance in all_lines:
            # Add stations to the set of all stations
            self.stations.add(station1)
            self.stations.add(station2)

            # Add edges to the graph (undirected graph)
            if station1 not in self.graph:
                self.graph[station1] = {}
            if station2 not in self.graph:
                self.graph[station2] = {}

            # Add the edge in both directions (undirected graph)
            self.graph[station1][station2] = distance
            self.graph[station2][station1] = distance

        # Map stations to their lines
        for line_name, stations in self.lines.items():
            for station in stations:
                if station not in self.station_lines:
                    self.station_lines[station] = []
                if line_name not in self.station_lines[station]:
                    self.station_lines[station].append(line_name)

    def get_all_stations(self) -> List[str]:
        """Return a sorted list of all stations in the network."""
        return sorted(list(self.stations))

    def get_popular_stations(self) -> List[str]:
        """Return list of popular/major interchange stations."""
        return [s for s in self.POPULAR_STATIONS if s in self.stations]

    def search_stations(self, query: str) -> List[str]:
        """Search stations by partial name match (case-insensitive)."""
        if not query or len(query) < 2:
            return []
        query_lower = query.lower()
        matches = [s for s in self.stations if query_lower in s.lower()]
        # Sort by relevance: stations starting with query first
        matches.sort(key=lambda s: (not s.lower().startswith(query_lower), s))
        return matches[:10]  # Return top 10 matches

    def get_interchange_stations(self) -> List[str]:
        """Return stations that connect multiple lines."""
        return sorted([s for s, lines in self.station_lines.items() if len(lines) > 1])

    def calculate_fare(self, distance: float, use_smart_card: bool = False) -> dict:
        """
        Calculate the fare based on the distance traveled.

        Delhi Metro fare structure (as of 2024):
        - Up to 2 km: ₹10
        - 2-5 km: ₹20
        - 5-12 km: ₹30
        - 12-21 km: ₹40
        - 21-32 km: ₹50
        - Above 32 km: ₹60

        Smart Card users get 10% discount on all fares.

        Args:
            distance: Distance in kilometers
            use_smart_card: Whether to apply smart card discount

        Returns:
            Dictionary with token_fare, smart_card_fare, and savings
        """
        # Calculate base token fare using DMRC's slab structure
        if distance <= 2:
            token_fare = 10
        elif distance <= 5:
            token_fare = 20
        elif distance <= 12:
            token_fare = 30
        elif distance <= 21:
            token_fare = 40
        elif distance <= 32:
            token_fare = 50
        else:  # Above 32 km
            token_fare = 60

        # Smart card users get 10% discount (rounded down)
        smart_card_fare = int(token_fare * 0.9)
        savings = token_fare - smart_card_fare

        return {
            "token_fare": token_fare,
            "smart_card_fare": smart_card_fare,
            "savings": savings,
            "recommended_fare": smart_card_fare if use_smart_card else token_fare,
        }

    def _normalize_station_name(self, name: str) -> str:
        """Normalize station name for matching."""
        if not isinstance(name, str):
            return ""
        return name.strip().lower()

    def _get_station_mapping(self) -> Dict[str, str]:
        """Create a mapping of normalized names to actual station names."""
        return {self._normalize_station_name(s): s for s in self.stations}

    def find_shortest_path(
        self, start: str, end: str
    ) -> Tuple[List[str], float, List[dict]]:
        """
        Find the shortest path between start and end stations using
        Dijkstra's algorithm with a min-heap for O(E log V) performance.

        How it works:
        1. Start at the source station with distance 0
        2. Visit the nearest unvisited station
        3. Update distances to all its neighbors
        4. Repeat until we reach the destination
        5. Reconstruct the path by backtracking

        Args:
            start: Starting station name
            end: Destination station name

        Returns:
            Tuple of (path, distance, line_changes)
        """
        if not start or not end:
            logger.error(f"Invalid station names: start='{start}', end='{end}'")
            return [], 0, []

        try:
            # Normalize station names (handle case sensitivity, spaces, etc.)
            station_map = self._get_station_mapping()
            start_norm = self._normalize_station_name(start)
            end_norm = self._normalize_station_name(end)

            # Validate that both stations exist in our network
            if start_norm not in station_map:
                logger.error(f"Start station not found: '{start}'")
                return [], 0, []
            if end_norm not in station_map:
                logger.error(f"End station not found: '{end}'")
                return [], 0, []

            # Get actual station names (with proper capitalization)
            start = station_map[start_norm]
            end = station_map[end_norm]

            if start not in self.graph or end not in self.graph:
                logger.error(f"Station not in graph: start='{start}', end='{end}'")
                return [], 0, []

            # === DIJKSTRA'S ALGORITHM IMPLEMENTATION ===

            # Step 1: Initialize distances (all stations start at infinity except source)
            distances = {station: float("infinity") for station in self.stations}
            distances[start] = 0

            # Step 2: Keep track of the path (which station did we come from?)
            previous = {station: None for station in self.stations}

            # Step 3: Priority queue - always process the nearest station first
            # Format: (distance_from_start, station_name)
            pq = [(0, start)]
            visited = set()

            # Step 4: Process stations in order of distance from start
            while pq:
                # Get the station with minimum distance
                current_dist, current = heapq.heappop(pq)

                # Skip if we've already processed this station
                # (heap may contain duplicates with different distances)
                if current in visited:
                    continue

                visited.add(current)

                # Optimization: Stop early if we've reached our destination
                if current == end:
                    break

                # Skip outdated entries (we found a better path already)
                if current_dist > distances[current]:
                    continue

                # Step 5: Update distances to all neighboring stations
                for neighbor, edge_distance in self.graph[current].items():
                    # Skip if we've already processed this neighbor
                    if neighbor in visited:
                        continue

                    # Calculate new distance via current station
                    new_distance = current_dist + edge_distance

                    # If this path is shorter than what we knew before, update it!
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current  # Remember how we got here
                        heapq.heappush(pq, (new_distance, neighbor))

            # Check if we actually found a path
            if distances[end] == float("infinity"):
                logger.warning(f"No path found from '{start}' to '{end}'")
                return [], 0, []

            # Step 6: Reconstruct the path by backtracking from end to start
            path = []
            current = end
            while current:
                path.append(current)
                current = previous[current]  # Go backwards through the path
            path.reverse()  # Flip it to go start -> end

            # Step 7: Figure out where we need to change metro lines
            line_changes = self._identify_line_changes(path)

            total_distance = round(distances[end], 2)
            logger.info(
                f"Route found: {len(path)} stations, {total_distance} km, {len(line_changes)} changes"
            )

            return path, total_distance, line_changes

        except Exception as e:
            logger.exception(f"Error finding path: {e}")
            return [], 0, []

    def find_route_least_changes(
        self, start: str, end: str
    ) -> Tuple[List[str], float, List[dict]]:
        """
        Find route with minimum line changes using modified BFS.
        Prioritizes staying on the same line over shorter distance.

        Args:
            start: Starting station name
            end: Destination station name

        Returns:
            Tuple of (path, distance, line_changes)
        """
        if not start or not end:
            return [], 0, []

        try:
            station_map = self._get_station_mapping()
            start_norm = self._normalize_station_name(start)
            end_norm = self._normalize_station_name(end)

            if start_norm not in station_map or end_norm not in station_map:
                return [], 0, []

            start = station_map[start_norm]
            end = station_map[end_norm]

            # BFS with state: (station, current_lines, changes_count)
            # Priority: (changes, distance, station, path, current_lines)
            pq = [(0, 0, start, [start], frozenset(self.station_lines.get(start, [])))]
            visited = {}  # station -> min changes to reach it

            while pq:
                changes, dist, current, path, current_lines = heapq.heappop(pq)

                if current == end:
                    line_changes = self._identify_line_changes(path)
                    return path, round(dist, 2), line_changes

                state_key = (current, current_lines)
                if state_key in visited and visited[state_key] <= changes:
                    continue
                visited[state_key] = changes

                for neighbor, edge_dist in self.graph[current].items():
                    if neighbor in path:  # Avoid cycles
                        continue

                    neighbor_lines = frozenset(self.station_lines.get(neighbor, []))
                    common_lines = current_lines & neighbor_lines

                    if common_lines:
                        # No line change needed
                        new_changes = changes
                        new_lines = common_lines
                    else:
                        # Line change required
                        new_changes = changes + 1
                        new_lines = neighbor_lines

                    new_path = path + [neighbor]
                    new_dist = dist + edge_dist

                    heapq.heappush(
                        pq, (new_changes, new_dist, neighbor, new_path, new_lines)
                    )

            return [], 0, []

        except Exception as e:
            logger.exception(f"Error finding least-changes route: {e}")
            return [], 0, []

    def find_all_routes(self, start: str, end: str) -> List[RouteResult]:
        """
        Find multiple route options between two stations.

        Returns routes optimized for:
        1. Shortest distance
        2. Least line changes

        Args:
            start: Starting station name
            end: Destination station name

        Returns:
            List of RouteResult objects with different optimization strategies
        """
        routes = []

        # Get shortest path
        path1, dist1, changes1 = self.find_shortest_path(start, end)
        if path1:
            routes.append(
                RouteResult(
                    path=path1,
                    distance=dist1,
                    line_changes=changes1,
                    route_type="shortest",
                )
            )

        # Get least changes path
        path2, dist2, changes2 = self.find_route_least_changes(start, end)
        if path2:
            # Only add if different from shortest path
            if path2 != path1:
                routes.append(
                    RouteResult(
                        path=path2,
                        distance=dist2,
                        line_changes=changes2,
                        route_type="least_changes",
                    )
                )

        return routes

    def _identify_line_changes(self, path: List[str]) -> List[dict]:
        """
        Identify all line changes in a given path.

        For example, if you go:
        Rajiv Chowk (Yellow) -> Patel Chowk (Yellow) -> Central Secretariat (Yellow + Violet)

        At Central Secretariat, you might switch from Yellow to Violet line.
        This function detects those switches.
        """
        line_changes = []
        current_lines = set()

        for i, station in enumerate(path):
            station_lines = set(self.station_lines.get(station, []))

            # First station - just record which lines are available
            if i == 0:
                current_lines = station_lines
                continue

            # Check if we can continue on the same line
            common_lines = current_lines & station_lines  # Set intersection

            # If no common lines, we MUST change (different lines)
            if not common_lines and current_lines and station_lines:
                line_changes.append(
                    {
                        "station": station,
                        "from_lines": list(current_lines),
                        "to_lines": list(station_lines),
                        "position": i,
                    }
                )
                current_lines = station_lines
            # If we can continue on same line, prefer that
            elif common_lines:
                current_lines = common_lines

        return line_changes

    def get_route_summary(
        self, path: List[str], distance: float, line_changes: List[dict]
    ) -> dict:
        """Generate a human-readable summary of a route."""
        if not path:
            return {"error": "No route available"}

        # Estimate travel time (average 2.5 min per station + 3 min per change)
        travel_time = len(path) * 2.5 + len(line_changes) * 3

        fare_info = self.calculate_fare(distance)

        return {
            "start": path[0],
            "end": path[-1],
            "stations_count": len(path),
            "distance_km": distance,
            "estimated_time_min": round(travel_time),
            "line_changes_count": len(line_changes),
            "fare": fare_info,
        }
