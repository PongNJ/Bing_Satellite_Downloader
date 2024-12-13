"""
Author: Natchapon Jongwiriyanurak
Email: ucesnjo@ucl.ac.uk


Description:
This script provides a utility function to calculate a bounding box around a given 
geographic coordinate (latitude, longitude) in WGS84 format. The bounding box is square, 
centered on the input coordinates, and defined by the specified box size in meters.

The function `calculate_bounding_box` takes the center point (latitude, longitude) and 
the side length of the bounding box in meters, and returns the coordinates of the 
upper-left and lower-right corners of the bounding box.

This script includes:
1. A function `calculate_bounding_box` to compute the bounding box.
2. An example usage section (`__main__`) that demonstrates the function's capability 
   with default and custom bounding box sizes.

Usage:
- Run this script directly to see example outputs for default and custom box sizes.
- Import the `calculate_bounding_box` function into other projects to use as a utility.

Parameters:
- Latitude (`lat`) and Longitude (`lon`): Center coordinates of the bounding box (WGS84).
- `box_size_meters`: The length of one side of the square bounding box in meters.

Returns:
- A tuple of four values:
  (lat1, lon1, lat2, lon2), where:
  - `lat1`, `lon1`: Upper-left corner of the bounding box.
  - `lat2`, `lon2`: Lower-right corner of the bounding box.

Example:
Default 200m box:
Input: Latitude = 13.7563, Longitude = 100.5018
Output: Upper-left(13.75710324531766, 100.50113513235514), 
        Lower-right(13.755496754682343, 100.50246486764487)

Custom 500m box:
Input: Latitude = 13.7563, Longitude = 100.5018
Output: Upper-left(13.75817596159415, 100.50033783088785), 
        Lower-right(13.754424038405849, 100.50326216911215)
"""


import math

def calculate_bounding_box(lat, lon, box_size_meters):
    """
    Calculate the left-up and right-down coordinates of a square bounding box (in WGS84).
    
    :param lat: Latitude of the center point in WGS84.
    :param lon: Longitude of the center point in WGS84.
    :param box_size_meters: Length of the box side in meters (default is 200m).
    :return: Tuple (lat1, lon1, lat2, lon2) for upper-left and lower-right corners.
    """
    # Earth's radius in meters
    R = 6378137

    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calculate the offsets in radians
    d_lat = box_size_meters / R
    d_lon = box_size_meters / (R * math.cos(lat_rad))

    # Calculate the corner coordinates
    lat1 = math.degrees(lat_rad + d_lat / 2)  # Upper-left latitude
    lon1 = math.degrees(lon_rad - d_lon / 2)  # Upper-left longitude
    lat2 = math.degrees(lat_rad - d_lat / 2)  # Lower-right latitude
    lon2 = math.degrees(lon_rad + d_lon / 2)  # Lower-right longitude

    return lat1, lon1, lat2, lon2

# Example usage
if __name__ == "__main__":
    # Default box size of 200 meters
    print("Default 200m box:")
    lat, lon = 13.7563, 100.5018  # Example for Bangkok
    print(calculate_bounding_box(lat, lon))

    # Custom box size of 500 meters
    print("\nCustom 500m box:")
    print(calculate_bounding_box(lat, lon, box_size_meters=500))
