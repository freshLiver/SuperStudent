from geopy.geocoders import Nominatim

# proj lib
from botlib.botlogger import BotLogger



class GeoAPI :
    """

    """
    geolocator = Nominatim(user_agent = "SuperStudentBot")


    @staticmethod
    def get_coordinate( address: str ) -> tuple :
        """

        :param address:
        :return:
        """
        location = GeoAPI.geolocator.geocode(address)
        coordinate = location.latitude, location.longitude

        BotLogger.debug(f"Coordinate Of {address} is {coordinate}")
        return coordinate


    @staticmethod
    def get_full_address( address: str ) -> str :
        """

        :param address:
        :return:
        """
        full_address = GeoAPI.geolocator.geocode(address).address

        BotLogger.debug(f"Full Address Of {address} is {full_address}")
        return full_address


if __name__ == '__main__' :
    res = GeoAPI.get_full_address("成大資訊新館")
    print(res)