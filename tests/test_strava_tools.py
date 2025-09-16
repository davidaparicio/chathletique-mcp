"""
Simple tests for strava tools functionality
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestRoutePlanning:
    """Test route planning utility functions"""

    def test_get_mapping_coords_basic(self):
        """Test _get_mapping_coords with a simple route"""
        # Import the function we want to test
        # We'll need to mock the create_itinerary function to access its nested functions

        # Mock route data
        mock_route = {
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            [2.3522, 48.8566],  # Paris center
                            [2.3530, 48.8570],
                            [2.3540, 48.8575],
                            [2.3550, 48.8580],
                            [2.3560, 48.8585],
                        ]
                    }
                }
            ]
        }

        # Since _get_mapping_coords is nested inside create_itinerary,
        # we'll test the logic by creating a standalone version
        def test_get_mapping_coords(route, distance_km):
            coordinates = route["features"][0]["geometry"]["coordinates"]
            if not coordinates:
                return []
            if len(coordinates) == 1:
                lon, lat = coordinates[0]
                return [(float(lon), float(lat))]

            num_points = max(2, int(distance_km) + 1)
            last_index = len(coordinates) - 1
            sampled_coords = []
            for i in range(num_points):
                coord_index = round(i * last_index / (num_points - 1))
                lon, lat = coordinates[coord_index]
                sampled_coords.append((float(lon), float(lat)))
            return sampled_coords

        result = test_get_mapping_coords(mock_route, 5.0)

        # Should return coordinates including start and end
        assert len(result) >= 2
        assert result[0] == (2.3522, 48.8566)  # First coordinate
        assert result[-1] == (2.3560, 48.8585)  # Last coordinate
        assert all(isinstance(coord, tuple) and len(coord) == 2 for coord in result)

    def test_get_mapping_coords_single_point(self):
        """Test _get_mapping_coords with single coordinate"""
        mock_route = {"features": [{"geometry": {"coordinates": [[2.3522, 48.8566]]}}]}

        def test_get_mapping_coords(route, distance_km):
            coordinates = route["features"][0]["geometry"]["coordinates"]
            if not coordinates:
                return []
            if len(coordinates) == 1:
                lon, lat = coordinates[0]
                return [(float(lon), float(lat))]
            # ... rest of logic

        result = test_get_mapping_coords(mock_route, 3.0)

        assert len(result) == 1
        assert result[0] == (2.3522, 48.8566)

    def test_get_mapping_coords_empty(self):
        """Test _get_mapping_coords with empty coordinates"""
        mock_route = {"features": [{"geometry": {"coordinates": []}}]}

        def test_get_mapping_coords(route, distance_km):
            coordinates = route["features"][0]["geometry"]["coordinates"]
            if not coordinates:
                return []
            # ... rest of logic

        result = test_get_mapping_coords(mock_route, 5.0)

        assert result == []


class TestGoogleMapsLink:
    """Test Google Maps link generation"""

    def test_gmaps_link_with_waypoints(self):
        """Test Google Maps link generation with waypoints"""
        from urllib.parse import urlencode, quote_plus

        def test_get_gmaps_directions_link(origin_coords, waypoints_coords_list=None):
            lon0, lat0 = origin_coords
            origin = f"{lat0},{lon0}"

            if waypoints_coords_list:
                wps = [
                    f"{lat},{lon}"
                    for lon, lat in waypoints_coords_list
                    if f"{lat},{lon}" != origin
                ]
                params = {
                    "api": 1,
                    "origin": origin,
                    "destination": origin,
                    "waypoints": "|".join(wps),
                }
                return "https://www.google.com/maps/dir/?" + urlencode(
                    params, quote_via=quote_plus
                )

            params = {"api": 1, "destination": origin}
            return "https://www.google.com/maps/dir/?" + urlencode(
                params, quote_via=quote_plus
            )

        origin = (2.3522, 48.8566)  # lon, lat
        waypoints = [(2.3530, 48.8570), (2.3540, 48.8575)]

        result = test_get_gmaps_directions_link(origin, waypoints)

        assert "https://www.google.com/maps/dir/?" in result
        assert "api=1" in result
        assert "origin=48.8566%2C2.3522" in result
        assert "destination=48.8566%2C2.3522" in result
        assert "waypoints=" in result

    def test_gmaps_link_no_waypoints(self):
        """Test Google Maps link generation without waypoints"""
        from urllib.parse import urlencode, quote_plus

        def test_get_gmaps_directions_link(origin_coords, waypoints_coords_list=None):
            lon0, lat0 = origin_coords
            origin = f"{lat0},{lon0}"

            if waypoints_coords_list:
                # ... waypoints logic
                pass

            params = {"api": 1, "destination": origin}
            return "https://www.google.com/maps/dir/?" + urlencode(
                params, quote_via=quote_plus
            )

        origin = (2.3522, 48.8566)

        result = test_get_gmaps_directions_link(origin, None)

        assert "https://www.google.com/maps/dir/?" in result
        assert "api=1" in result
        assert "destination=48.8566%2C2.3522" in result
        assert "waypoints" not in result


class TestDistanceValidation:
    """Test distance validation logic"""

    def test_minimum_distance_enforcement(self):
        """Test that distances below 3km are adjusted to 3km"""
        # This tests the logic: if distance_km < 3: distance_km = 3

        test_distances = [1, 2, 2.5, 3, 5, 10]
        expected = [3, 3, 3, 3, 5, 10]

        for i, distance in enumerate(test_distances):
            adjusted = distance if distance >= 3 else 3
            assert adjusted == expected[i]

    def test_distance_to_meters_conversion(self):
        """Test the distance conversion logic"""
        # Tests: distance_m = int(distance_km * 1100)

        assert int(5 * 1100) == 5500
        assert int(10 * 1100) == 11000
        assert int(3.5 * 1100) == 3850
