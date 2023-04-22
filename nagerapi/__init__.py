import logging, pkg_resources
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Union
from requests import Session
from requests.exceptions import RequestException

try:
    __version__ = pkg_resources.get_distribution("nagerapi").version
except pkg_resources.DistributionNotFound:
    __version__ = ""
__author__ = "Nathan Taggart"
__credits__ = "meisnate12"
__package_name__ = "nagerapi"
__project_name__ = "NagerAPI"
__description__ = "Python wrapper for Nager API https://date.nager.at/Api"
__url__ = "https://github.com/meisnate12/NagerAPI"
__email__ = 'meisnate12@gmail.com'
__license__ = 'MIT License'
__all__ = ["NagerObjectAPI", "NagerRawAPI", "NagerException", "Country", "Weekend", "Holiday"]
base_url = "https://date.nager.at/api/v3/"

logger = logging.getLogger(__name__)


class NagerException(Exception):
    """ Base class for all Nagar exceptions. """
    pass


class NagerBase:
    def __init__(self, nager):
        self._nager = nager
        self._loading = True

    def __setattr__(self, key, value):
        if key.startswith("_") or self._loading:
            super().__setattr__(key, value)
        else:
            raise AttributeError("Attributes cannot be edited")

    def __repr__(self):
        return self.__str__()


class Weekend(NagerBase):
    """ Represents a single Long Weekend.

        Attributes:
            start_date (datetime): Start Date of the Long Weekend.
            end_date (datetime): End Date of the Long Weekend.
            day_count (int): Days in the Long Weekend.
            need_bridge_day (bool): Is a Bridge Day needed for the Long Weekend.
    """
    def __init__(self, nager, data):
        super().__init__(nager)
        self.start_date = datetime.strptime(data["startDate"], "%Y-%m-%d") if data["startDate"] else None
        self.end_date = datetime.strptime(data["endDate"], "%Y-%m-%d") if data["endDate"] else None
        self.day_count = data["dayCount"]
        self.need_bridge_day = data["needBridgeDay"]
        self._loading = False

    def __str__(self):
        return f"{self.start_date.strftime('%Y-%m-%d')} --> {self.end_date.strftime('%Y-%m-%d')}"


class Holiday(NagerBase):
    """ Represents a single Holiday.

        Attributes:
            name (str): English Name of the Holiday.
            local_name (str): Local name of the Holiday.
            date (datetime): Date of the Holiday.
            code (str): ISO 3166-1 alpha-2 Country Code for the Holiday.
            country (Country): Country Object for the ISO 3166-1 alpha-2 Country Code.
            fixed_holiday (bool): Is this public holiday every year on the same date.
            global_holiday (bool): Is this public holiday in every county (Federal State).
            counties (List[str]): List of Counties (ISO-3166-2 - Federal States).
            launch_year (int): The launch year of the public holiday.
            types (List[str]): A list of types the public holiday it is valid.
            is_public (bool): "Public" type is in types.
            is_bank (bool): "Bank" type is in types.
            is_school (bool): "School" type is in types.
            is_authorities (bool): "Authorities" type is in types.
            is_optional (bool): "Optional" type is in types.
            is_observance (bool): "Observance" type is in types.

    """
    def __init__(self, nager, data):
        super().__init__(nager)
        self.name = data["name"]
        self.local_name = data["localName"]
        self.date = datetime.strptime(data["date"], "%Y-%m-%d") if data["date"] else None
        self.code = data["countryCode"]
        self.country = self._nager.country(self.code, load=False)
        self.fixed_holiday = data["fixed"]
        self.global_holiday = data["global"]
        self.counties = data["counties"]
        self.launch_year = data["launchYear"]
        self.types = data["types"]
        self.is_public = "Public" in self.types
        self.is_bank = "Bank" in self.types
        self.is_school = "School" in self.types
        self.is_authorities = "Authorities" in self.types
        self.is_optional = "Optional" in self.types
        self.is_observance = "Observance" in self.types
        self._loading = False

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%Y-%m-%d')})"


class Country(NagerBase):
    """ Represents a single Holiday.

        Attributes:
            name (str): Common Name of the Country.
            code (str): ISO 3166-1 alpha-2 Country Code.
            official (str): Official Name of the Country.
            region (str): Region of the Country.
            borders (List[Country]): List of Counties the border the Country.

    """
    def __init__(self, nager, data):
        super().__init__(nager)
        self._load(data)

    def _load(self, data):
        self._loading = True
        self.name = data["name"] if "name" in data else data["commonName"]
        self.code = data["countryCode"]
        self.official = data["officialName"] if "officialName" in data else None
        self.region = data["region"] if "region" in data else None
        self.borders = [Country(self._nager, c) for c in data["borders"]] if "borders" in data and data["borders"] else None
        self._full = "region" in data
        self._loading = False

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if type(self) is type(other):
            return self.name == other.name and self.code == other.code
        else:
            return str(self.code) == str(other).upper()

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        if value is not None or self._full:
            return value
        self.load_details()
        return super().__getattribute__(item)

    def load_details(self):
        """ Loads the details for the country. """
        self._load(self._nager.api.get_country_info(self.code))

    def long_weekends(self, year: int):
        """ Alias for :meth:`~NagerObjectAPI.long_weekends` for this country. """
        return [Weekend(self._nager, w) for w in self._nager.api.get_long_weekend(year, self.code)]

    def public_holidays(self, year: int):
        """ Alias for :meth:`~NagerObjectAPI.public_holidays` for this country. """
        return [Holiday(self._nager, h) for h in self._nager.api.get_public_holidays(year, self.code)]

    def is_today_public_holiday(self):
        """ Alias for :meth:`~NagerObjectAPI.is_today_public_holiday` for this country. """
        return self._nager.api.get_is_today_public_holiday()

    def next_public_holidays(self):
        """ Alias for :meth:`~NagerObjectAPI.next_public_holidays` for this country. """
        return [Holiday(self._nager, h) for h in self._nager.api.get_next_public_holidays(self.code)]


class NagerObjectAPI:
    """ Main Object API Class

        Parameters:
            session (Session): Use your own Session object.
            default_country (Union[str, Country]): Default Country to use in any method where country isn't provided.

        Attributes:
            name (str): Name of the API.
            version (int): Version of the API.
            default_country (Country): Default Country to use.
    """
    def __init__(self, session: Session = None, default_country: Union[str, Country] = None):
        self._loading = True
        self.api = NagerRawAPI(session=session)
        data = self.api.get_version()
        self.name = data["name"]
        self.version = data["version"]
        self._countries = None
        self.default_country = self.country(default_country) if default_country else None # noqa
        self._loading = False

    def __setattr__(self, key, value):
        if key.startswith("_") or self._loading:
            super().__setattr__(key, value)
        else:
            raise AttributeError("Attributes cannot be edited")

    def country(self, country: Union[Country, str] = None, load=True):
        """ :class:`~Country` Object with details.

            Parameters:
                country (Union[Country, str]): ISO 3166-1 alpha-2 Country Code.
                load (bool): Load Full Details.

            Returns:
                :class:`~Country`

            Raises:
                :class:`NagerException`: When an Invalid Country Code is provided.
        """
        if not country:
            if not self.default_country:
                raise NagerException("No Country Provided")
            country = self.default_country
        if not isinstance(country, Country):
            code = str(country).upper()
            if code not in self.available_countries:
                raise NagerException(f"Invalid Country Code: {code}. Options: {[c for c in self.available_countries]}")
            country = self.available_countries[self.available_countries.index(code)] # noqa
        if not country._full and load: # noqa
            country.load_details()
        return country

    @property
    def available_countries(self):
        """ All available :class:`~Country` objects.

            Returns:
                List[:class:`~Country`]
        """
        if self._countries is None:
            self._countries = [Country(self, c) for c in self.api.get_available_countries()]
        return self._countries

    def long_weekends(self, year: int, country: Union[Country, str] = None):
        """ All available :class:`~Weekend` Objects for a country in a given year.

            Parameters:
                year (int): Year to look at.
                country (Union[Country, str]): ISO 3166-1 alpha-2 Country Code.

            Returns:
                List[:class:`~Weekend`]

            Raises:
                :class:`NagerException`: When an Invalid Country Code or year is provided.
        """
        return self.country(country, load=False).long_weekends(year)

    def public_holidays(self, year: int, country: Union[Country, str] = None):
        """ All available public :class:`~Holiday` Objects for a country in a given year.

            Parameters:
                year (int): Year to look at.
                country (Union[Country, str]): ISO 3166-1 alpha-2 Country Code.

            Returns:
                List[:class:`~Holiday`]

            Raises:
                :class:`NagerException`: When an Invalid Country Code or year is provided.
        """
        return self.country(country, load=False).public_holidays(year)

    def is_today_public_holiday(self, country: Union[Country, str] = None):
        """ Is today a public Holiday for the given country.

            Parameters:
                country (Union[Country, str]): ISO 3166-1 alpha-2 Country Code.

            Returns:
                bool

            Raises:
                :class:`NagerException`: When an Invalid Country Code is provided.
        """
        return self.country(country, load=False).is_today_public_holiday()

    def next_public_holidays(self, country: Union[Country, str] = None):
        """ Returns the upcoming public :class:`~Holiday` Objects for the next 365 days for the given country.

            Parameters:
                country (Union[Country, str]): ISO 3166-1 alpha-2 Country Code.

            Returns:
                List[:class:`~Holiday`]

            Raises:
                :class:`NagerException`: When an Invalid Country Code is provided.
        """
        return self.country(country, load=False).next_public_holidays()

    def next_public_worldwide_holidays(self):
        """ Returns the upcoming public :class:`~Holiday` Objects for the next 7 days.

            Returns:
                List[:class:`~Holiday`]
        """
        return [Holiday(self, h) for h in self.api.get_next_public_worldwide_holidays()]


class NagerRawAPI:
    """ Main Raw API Class

        Parameters:
            session (Session): Use your own Session object.
    """
    def __init__(self, session: Session = None):
        self._session = Session() if session is None else session

    def _request(self, request_url, status_bool=False, **kwargs):
        """ process request. """
        url_params = {}
        for key, value in kwargs.items():
            if value is not None:
                url_params[key] = value
        logger.debug(f"Request URL: {request_url}")
        if url_params:
            logger.debug(f"Request Params: {url_params}")
        try:
            self.response = self._session.get(request_url, params=url_params)
        except RequestException as e:
            raise NagerException(f"Failed to Connect to {request_url}: {e}")
        if status_bool:
            if self.response.status_code == 200:
                return True
            elif self.response.status_code == 204:
                return False
        try:
            response_json = self.response.json()
        except JSONDecodeError as e:
            raise NagerException(f"Failed to Decode Response JSON{request_url}: {e}\nContent: {self.response.content}")
        logger.debug(f"Response ({self.response.status_code} [{self.response.reason}]) {response_json}")

        if self.response.status_code == 404:
            raise NagerException(f"({self.response.status_code} [{self.response.reason}]) Country Code Invalid")
        elif self.response.status_code >= 400:
            raise NagerException(f"({self.response.status_code} [{self.response.reason}]) {response_json}")
        return response_json

    def get_country_info(self, country: str):
        """ `GET CountryInfo <https://date.nager.at/swagger/index.html>`__: Get country info for the given country.

            Parameters:
                country (str): ISO 3166-1 alpha-2 Country Code.

            Returns:
                Dict

            Raises:
                :class:`NagerException`: When an Invalid Country Code or year is provided.
        """
        return self._request(f"{base_url}CountryInfo/{country}")

    def get_available_countries(self):
        """ `GET AvailableCountries <https://date.nager.at/swagger/index.html>`__: Get all available countries.

            Returns:
                List[Dict]
        """
        return self._request(f"{base_url}AvailableCountries")

    def get_long_weekend(self, year: int, country: str):
        """ `GET LongWeekend <https://date.nager.at/swagger/index.html>`__: Get long weekends for a given country

            Parameters:
                year (int): Year to look at.
                country (str): ISO 3166-1 alpha-2 Country Code.

            Returns:
                List[Dict]

            Raises:
                :class:`NagerException`: When an Invalid Country Code or year is provided.
        """
        return self._request(f"{base_url}LongWeekend/{year}/{country}")

    def get_public_holidays(self, year: int, country: str):
        """ `GET PublicHolidays <https://date.nager.at/swagger/index.html>`__: Get public holidays.

            Parameters:
                year (int): Year to look at.
                country (str): ISO 3166-1 alpha-2 Country Code.

            Returns:
                List[Dict]

            Raises:
                :class:`NagerException`: When an Invalid Country Code or year is provided.
        """
        return self._request(f"{base_url}PublicHolidays/{year}/{country}")

    def get_is_today_public_holiday(self, country: str):
        """ `GET IsTodayPublicHoliday <https://date.nager.at/swagger/index.html>`__: Is today a public holiday.

            Parameters:
                country (str): ISO 3166-1 alpha-2 Country Code.

            Returns:
                bool

            Raises:
                :class:`NagerException`: When an Invalid Country Code is provided.
        """
        return self._request(f"{base_url}IsTodayPublicHoliday/{country}", status_bool=True)

    def get_next_public_holidays(self, country: str):
        """ `GET NextPublicHolidays <https://date.nager.at/swagger/index.html>`__: Returns the upcoming public holidays for the next 365 days for the given country.

            Parameters:
                country (str): ISO 3166-1 alpha-2 Country Code.

            Returns:
                List[Dict]

            Raises:
                :class:`NagerException`: When an Invalid Country Code is provided.
        """
        return self._request(f"{base_url}NextPublicHolidays/{country}")

    def get_next_public_worldwide_holidays(self):
        """ `GET NextPublicHolidaysWorldwide <https://date.nager.at/swagger/index.html>`__: Returns the upcoming public holidays for the next 7 days.

            Returns:
                List[Dict]
        """
        return self._request(f"{base_url}NextPublicHolidaysWorldwide")

    def get_version(self):
        """ `GET Version <https://date.nager.at/swagger/index.html>`__: Get version of the used Nager.Date library.

            Returns:
                Dict
        """
        return self._request(f"{base_url}Version")
