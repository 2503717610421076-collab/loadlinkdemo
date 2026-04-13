def get_route_estimate(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng):
    """
    Mock function for Google Maps routing.
    In production, this would call the Google Maps Route API.
    """
    # Mock distance and duration
    return {
        "distance_km": 15.5,
        "duration_mins": 35
    }
