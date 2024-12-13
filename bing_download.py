import os
from urllib import request
from PIL import Image
from tilesystem import TileSystem

BASEURL = "http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131"
IMAGEMAXSIZE = 8192 * 8192 * 8  # Maximum width/height in pixels for the retrieved image
TILESIZE = 256  # In Bing tile system, one tile image is 256x256 pixels


class AerialImageRetrieval:
    """Class for aerial image retrieval for multiple coordinates."""

    def __init__(self, coords, size_meters=200):
        """
        Initialize with coordinates and size of the image in meters.
        Args:
            coords (list of tuples): A list of (latitude, longitude) pairs.
            size_meters (int): The size of the square image to retrieve in meters (default: 200m x 200m).
        """
        self.coords = coords
        self.size_meters = size_meters
        self.tgtfolder = './output/'
        os.makedirs(self.tgtfolder, exist_ok=True)

    def download_image(self, quadkey):
        """Download a tile image given the quadkey from Bing tile system."""
        with request.urlopen(BASEURL.format(quadkey)) as file:
            return Image.open(file)

    def is_valid_image(self, image):
        """Check whether the downloaded image is valid."""
        if not os.path.exists('null.png'):
            nullimg = self.download_image('11111111111111111111')
            nullimg.save('./null.png')
        return not (image == Image.open('./null.png'))

    def calculate_bounding_box(self, lat, lon):
        """Calculate a 200m x 200m bounding box centered at the given lat/lon."""
        level = TileSystem.MAXLEVEL
        ground_res = TileSystem.ground_resolution(lat, level)
        half_size_pixels = (self.size_meters / 2) / ground_res  # Convert meters to pixels

        # Get pixel coordinates for the center
        center_pixelX, center_pixelY = TileSystem.latlong_to_pixelXY(lat, lon, level)

        # Calculate bounding box in pixel coordinates
        pixelX1 = center_pixelX - half_size_pixels
        pixelX2 = center_pixelX + half_size_pixels
        pixelY1 = center_pixelY - half_size_pixels
        pixelY2 = center_pixelY + half_size_pixels

        # Clip pixel coordinates to the map size at the current level
        map_size = TileSystem.map_size(level)
        pixelX1 = TileSystem.clip(pixelX1, 0, map_size - 1)
        pixelX2 = TileSystem.clip(pixelX2, 0, map_size - 1)
        pixelY1 = TileSystem.clip(pixelY1, 0, map_size - 1)
        pixelY2 = TileSystem.clip(pixelY2, 0, map_size - 1)

        # Debugging log
        print(f"Clipped Pixels: X1={pixelX1}, Y1={pixelY1}, X2={pixelX2}, Y2={pixelY2}")

        # Convert bounding box back to lat/lon
        lat1, lon1 = TileSystem.pixelXY_to_latlong(pixelX1, pixelY1, level)
        lat2, lon2 = TileSystem.pixelXY_to_latlong(pixelX2, pixelY2, level)

        # Debugging log
        print(f"Calculated Bounding Box: Lat1={lat1}, Lon1={lon1}, Lat2={lat2}, Lon2={lon2}")

        return lat1, lon1, lat2, lon2

    def max_resolution_imagery_retrieval(self, lat1, lon1, lat2, lon2):
        """Retrieve the maximum resolution image for the given bounding box."""
        for level in range(TileSystem.MAXLEVEL, 0, -1):
            pixelX1, pixelY1 = TileSystem.latlong_to_pixelXY(lat1, lon1, level)
            pixelX2, pixelY2 = TileSystem.latlong_to_pixelXY(lat2, lon2, level)

            if abs(pixelX1 - pixelX2) <= 1 or abs(pixelY1 - pixelY2) <= 1:
                print("Cannot find a valid aerial imagery for the given bounding box!")
                return False

            tileX1, tileY1 = TileSystem.pixelXY_to_tileXY(pixelX1, pixelY1)
            tileX2, tileY2 = TileSystem.pixelXY_to_tileXY(pixelX2, pixelY2)

            result = Image.new('RGB', ((tileX2 - tileX1 + 1) * TILESIZE, (tileY2 - tileY1 + 1) * TILESIZE))
            for tileY in range(tileY1, tileY2 + 1):
                imagelist = []
                for tileX in range(tileX1, tileX2 + 1):
                    quadkey = TileSystem.tileXY_to_quadkey(tileX, tileY, level)
                    image = self.download_image(quadkey)
                    if self.is_valid_image(image):
                        imagelist.append(image)
                    else:
                        print(f"Cannot find tile image at level {level} for tile coordinate ({tileX}, {tileY})")
                        return False
                row_image = Image.new('RGB', (len(imagelist) * TILESIZE, TILESIZE))
                for i, image in enumerate(imagelist):
                    row_image.paste(image, (i * TILESIZE, 0))
                result.paste(row_image, (0, (tileY - tileY1) * TILESIZE))

            filename = os.path.join(self.tgtfolder, f'aerialImage_{lat1}_{lon1}.jpeg')
            result.save(filename)
            print(f"Image saved: {filename}")
            return True
        return False

    def retrieve_images(self):
        """Retrieve images for all coordinates."""
        for lat, lon in self.coords:
            lat1, lon1, lat2, lon2 = self.calculate_bounding_box(lat, lon)
            print(f"Processing location: {lat}, {lon}")
            success = self.max_resolution_imagery_retrieval(lat1, lon1, lat2, lon2)
            if not success:
                print(f"Failed to retrieve image for location: {lat}, {lon}")


def main():
    """Main function to handle input and start image retrieval."""
    coords = [(13.736717, 100.523186)]  # Example coordinates
    retrieval = AerialImageRetrieval(coords)
    retrieval.retrieve_images()


if __name__ == '__main__':
    main()
