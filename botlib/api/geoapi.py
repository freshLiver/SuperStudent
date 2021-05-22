from geopy.geocoders import Nominatim

# proj lib
from botlib.botlogger import BotLogger



class GeoApi :
    """

    """
    geo_locator = Nominatim(user_agent = "SuperStudentBot")


    @staticmethod
    def get_coordinate( address: str ) -> tuple or None :
        """

        :param address:
        :return:
        """
        location = GeoApi.geo_locator.geocode(address, country_codes = "tw")

        if location is None :
            return None

        # if this location exists, get coordinate
        coordinate = location.latitude, location.longitude

        BotLogger.debug(f"Coordinate Of {address} is {coordinate}")
        return coordinate


    @staticmethod
    def get_full_address( address: str ) -> str or None :
        """

        :param address: location string
        :return:
        """
        location = GeoApi.geo_locator.geocode(address, country_codes = "tw")

        if location is None :
            return None

        # if this location exists, get full address string
        full_address = location.address
        BotLogger.debug(f"Full Address Of {address} is {full_address}")
        return full_address


if __name__ == '__main__' :

    location = "清華大學"

    address = GeoApi.get_full_address(location)
    coordinate = GeoApi.get_coordinate(location)

    print(address)
    print(coordinate)