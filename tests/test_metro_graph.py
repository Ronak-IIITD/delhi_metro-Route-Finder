"""
Unit Tests for Delhi Metro Route Finder
Tests for core routing logic, fare calculation, and edge cases.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metro_graph import MetroGraph, RouteResult


class TestMetroGraphInitialization:
    """Tests for MetroGraph initialization and data integrity."""
    
    @pytest.fixture
    def metro(self):
        """Create a MetroGraph instance for testing."""
        return MetroGraph()
    
    def test_initialization(self, metro):
        """Test that MetroGraph initializes with stations."""
        assert len(metro.stations) > 0
        assert len(metro.graph) > 0
        assert len(metro.lines) > 0
    
    def test_station_count(self, metro):
        """Test that we have a reasonable number of stations."""
        station_count = len(metro.stations)
        assert station_count >= 200, f"Expected at least 200 stations, got {station_count}"
    
    def test_popular_stations_exist(self, metro):
        """Test that popular stations are in the network."""
        popular = metro.get_popular_stations()
        assert len(popular) > 0
        
        # Check specific important stations
        important_stations = ["Rajiv Chowk", "Kashmere Gate", "New Delhi"]
        for station in important_stations:
            assert station in metro.stations, f"Missing important station: {station}"
    
    def test_all_stations_have_connections(self, metro):
        """Test that all stations have at least one connection."""
        for station in metro.stations:
            connections = metro.graph.get(station, {})
            assert len(connections) >= 1, f"Station {station} has no connections"
    
    def test_interchange_stations(self, metro):
        """Test that interchange stations have multiple lines."""
        interchanges = metro.get_interchange_stations()
        assert len(interchanges) > 0
        
        # Check that Rajiv Chowk is an interchange (Yellow + Blue)
        rajiv_chowk_lines = metro.station_lines.get("Rajiv Chowk", [])
        assert len(rajiv_chowk_lines) >= 2, "Rajiv Chowk should have multiple lines"


class TestFareCalculation:
    """Tests for fare calculation logic."""
    
    @pytest.fixture
    def metro(self):
        return MetroGraph()
    
    def test_fare_structure_0_2km(self, metro):
        """Test fare for 0-2 km."""
        fare = metro.calculate_fare(1.5)
        assert fare['token_fare'] == 10
        assert fare['smart_card_fare'] == 9
        assert fare['savings'] == 1
    
    def test_fare_structure_2_5km(self, metro):
        """Test fare for 2-5 km."""
        fare = metro.calculate_fare(3.5)
        assert fare['token_fare'] == 20
        assert fare['smart_card_fare'] == 18
    
    def test_fare_structure_5_12km(self, metro):
        """Test fare for 5-12 km."""
        fare = metro.calculate_fare(8.0)
        assert fare['token_fare'] == 30
    
    def test_fare_structure_12_21km(self, metro):
        """Test fare for 12-21 km."""
        fare = metro.calculate_fare(15.0)
        assert fare['token_fare'] == 40
    
    def test_fare_structure_21_32km(self, metro):
        """Test fare for 21-32 km."""
        fare = metro.calculate_fare(25.0)
        assert fare['token_fare'] == 50
    
    def test_fare_structure_above_32km(self, metro):
        """Test fare for above 32 km."""
        fare = metro.calculate_fare(40.0)
        assert fare['token_fare'] == 60
    
    def test_smart_card_discount(self, metro):
        """Test that smart card always gives 10% discount."""
        for distance in [1, 3, 7, 15, 25, 40]:
            fare = metro.calculate_fare(distance)
            assert fare['smart_card_fare'] == int(fare['token_fare'] * 0.9)
    
    def test_fare_boundary_2km(self, metro):
        """Test fare at 2km boundary."""
        fare_2 = metro.calculate_fare(2.0)
        fare_2_1 = metro.calculate_fare(2.1)
        assert fare_2['token_fare'] == 10
        assert fare_2_1['token_fare'] == 20


class TestRouteFinding:
    """Tests for route finding algorithms."""
    
    @pytest.fixture
    def metro(self):
        return MetroGraph()
    
    def test_same_station_returns_single_station(self, metro):
        """Test that searching from a station to itself returns empty path."""
        path, distance, changes = metro.find_shortest_path("Rajiv Chowk", "Rajiv Chowk")
        # Same station should return empty or single station path
        assert len(path) <= 1
    
    def test_adjacent_stations(self, metro):
        """Test route between adjacent stations."""
        # Rajiv Chowk to Patel Chowk (adjacent on Yellow Line)
        path, distance, changes = metro.find_shortest_path("Rajiv Chowk", "Patel Chowk")
        assert len(path) == 2
        assert path[0] == "Rajiv Chowk"
        assert path[1] == "Patel Chowk"
        assert distance > 0
        assert len(changes) == 0  # No line changes needed
    
    def test_route_same_line(self, metro):
        """Test route staying on the same line."""
        # Both on Yellow Line
        path, distance, changes = metro.find_shortest_path("Rajiv Chowk", "Central Secretariat")
        assert len(path) > 0
        assert path[0] == "Rajiv Chowk"
        assert path[-1] == "Central Secretariat"
    
    def test_route_with_line_change(self, metro):
        """Test route requiring a line change."""
        # Yellow to Blue requires change at Rajiv Chowk
        path, distance, changes = metro.find_shortest_path("Chandni Chowk", "Barakhamba Road")
        assert len(path) > 0
        assert path[0] == "Chandni Chowk"
        assert path[-1] == "Barakhamba Road"
    
    def test_nonexistent_station(self, metro):
        """Test handling of non-existent station."""
        path, distance, changes = metro.find_shortest_path("Fake Station", "Rajiv Chowk")
        assert len(path) == 0
        assert distance == 0
    
    def test_case_insensitive_search(self, metro):
        """Test that station search is case-insensitive."""
        path1, dist1, _ = metro.find_shortest_path("RAJIV CHOWK", "new delhi")
        path2, dist2, _ = metro.find_shortest_path("Rajiv Chowk", "New Delhi")
        assert path1 == path2
        assert dist1 == dist2
    
    def test_distance_is_positive(self, metro):
        """Test that distances are always positive."""
        path, distance, _ = metro.find_shortest_path("Rajiv Chowk", "Kashmere Gate")
        assert distance > 0
    
    def test_path_continuity(self, metro):
        """Test that the path is continuous (each station connects to next)."""
        path, _, _ = metro.find_shortest_path("Dwarka Sector 21", "Noida City Centre")
        
        for i in range(len(path) - 1):
            current = path[i]
            next_station = path[i + 1]
            assert next_station in metro.graph[current], \
                f"Path discontinuity: {current} not connected to {next_station}"


class TestAlternativeRoutes:
    """Tests for alternative route finding."""
    
    @pytest.fixture
    def metro(self):
        return MetroGraph()
    
    def test_find_all_routes_returns_results(self, metro):
        """Test that find_all_routes returns at least one route."""
        routes = metro.find_all_routes("Rajiv Chowk", "Kashmere Gate")
        assert len(routes) >= 1
    
    def test_route_result_structure(self, metro):
        """Test that RouteResult has correct structure."""
        routes = metro.find_all_routes("Rajiv Chowk", "Kashmere Gate")
        
        for route in routes:
            assert isinstance(route, RouteResult)
            assert isinstance(route.path, list)
            assert isinstance(route.distance, (int, float))
            assert isinstance(route.line_changes, list)
            assert route.route_type in ['shortest', 'least_changes']
    
    def test_least_changes_route(self, metro):
        """Test that least_changes route minimizes line changes."""
        path1, dist1, changes1 = metro.find_shortest_path("Dwarka Sector 21", "Botanical Garden")
        path2, dist2, changes2 = metro.find_route_least_changes("Dwarka Sector 21", "Botanical Garden")
        
        # Least changes should have <= changes than shortest path
        # (or equal if they're the same route)
        assert len(changes2) <= len(changes1) or dist2 >= dist1


class TestStationSearch:
    """Tests for station search functionality."""
    
    @pytest.fixture
    def metro(self):
        return MetroGraph()
    
    def test_search_returns_results(self, metro):
        """Test that search returns results for valid query."""
        results = metro.search_stations("Rajiv")
        assert len(results) > 0
        assert "Rajiv Chowk" in results
    
    def test_search_case_insensitive(self, metro):
        """Test that search is case-insensitive."""
        results1 = metro.search_stations("rajiv")
        results2 = metro.search_stations("RAJIV")
        assert results1 == results2
    
    def test_search_partial_match(self, metro):
        """Test partial matching in search."""
        results = metro.search_stations("Dwarka")
        assert len(results) > 1  # Multiple Dwarka stations
    
    def test_search_short_query(self, metro):
        """Test that very short queries return empty."""
        results = metro.search_stations("R")
        assert len(results) == 0
    
    def test_search_no_results(self, metro):
        """Test search with no matching stations."""
        results = metro.search_stations("XYZABC")
        assert len(results) == 0
    
    def test_search_result_limit(self, metro):
        """Test that search results are limited."""
        results = metro.search_stations("Sector")
        assert len(results) <= 10  # Should be limited to 10


class TestRouteSummary:
    """Tests for route summary generation."""
    
    @pytest.fixture
    def metro(self):
        return MetroGraph()
    
    def test_summary_structure(self, metro):
        """Test that summary has all required fields."""
        path, distance, changes = metro.find_shortest_path("Rajiv Chowk", "Kashmere Gate")
        summary = metro.get_route_summary(path, distance, changes)
        
        assert 'start' in summary
        assert 'end' in summary
        assert 'stations_count' in summary
        assert 'distance_km' in summary
        assert 'estimated_time_min' in summary
        assert 'fare' in summary
    
    def test_summary_values(self, metro):
        """Test that summary values are correct."""
        path, distance, changes = metro.find_shortest_path("Rajiv Chowk", "Kashmere Gate")
        summary = metro.get_route_summary(path, distance, changes)
        
        assert summary['start'] == "Rajiv Chowk"
        assert summary['end'] == "Kashmere Gate"
        assert summary['stations_count'] == len(path)
        assert summary['distance_km'] == distance
    
    def test_empty_path_summary(self, metro):
        """Test summary with empty path."""
        summary = metro.get_route_summary([], 0, [])
        assert 'error' in summary


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.fixture
    def metro(self):
        return MetroGraph()
    
    def test_none_input(self, metro):
        """Test handling of None inputs."""
        path, distance, changes = metro.find_shortest_path(None, "Rajiv Chowk")
        assert len(path) == 0
        
        path, distance, changes = metro.find_shortest_path("Rajiv Chowk", None)
        assert len(path) == 0
    
    def test_empty_string_input(self, metro):
        """Test handling of empty string inputs."""
        path, distance, changes = metro.find_shortest_path("", "Rajiv Chowk")
        assert len(path) == 0
    
    def test_whitespace_input(self, metro):
        """Test handling of whitespace inputs."""
        path, distance, changes = metro.find_shortest_path("  Rajiv Chowk  ", "  Kashmere Gate  ")
        assert len(path) > 0  # Should trim and work
    
    def test_special_characters_in_station_name(self, metro):
        """Test stations with special characters."""
        # Some station names have special characters like "R.K Puram"
        if "R.K Puram" in metro.stations:
            path, distance, changes = metro.find_shortest_path("R.K Puram", "IIT Delhi")
            assert len(path) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
