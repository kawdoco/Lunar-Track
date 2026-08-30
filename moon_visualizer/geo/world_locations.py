"""
geo/world_locations.py
-------------------------
A bundled, offline gazetteer: (name, latitude, longitude, IANA timezone)
for essentially every country/territory on Earth, keyed by its capital
city. This is what makes the location search box able to jump to "any
location" the user types - Nepal, Fiji, Botswana, whatever - instead of
only the half-dozen hand-picked cities the map used to offer.

# OOP concept: MODULE-LEVEL DATA, NOT A CLASS
# ---------------------------------------------------------------------
# This is plain, static reference data (it never changes at runtime and
# nothing about it needs hiding behind methods), so - same reasoning as
# STYLE_SHEET in theme.py - it stays a simple module-level structure
# instead of being wrapped in a class that would only ever have one,
# never-mutated "instance".

Coordinates are the capital city's approximate position (a few
kilometres of precision is plenty for picking a point on a small map or
seeding a timezone lookup) - this is a convenience gazetteer, not a
survey-grade atlas.
"""

from __future__ import annotations

from typing import NamedTuple


class WorldLocation(NamedTuple):
    """One searchable place: a display name plus everything needed to
    apply it as an observer location (lat/lon) and a timezone guess."""

    name: str
    latitude_deg: float
    longitude_deg: float
    timezone: str


# A handful of "starred" favourites shown as one-click chips (kept in
# sync with the previous hardcoded preset list) - everything else is
# reachable through the search box instead of its own chip.
FAVORITE_LOCATIONS: list[WorldLocation] = [
    WorldLocation("Colombo, Sri Lanka", 6.9271, 79.8612, "Asia/Colombo"),
    WorldLocation("Kandy, Sri Lanka", 7.2906, 80.6337, "Asia/Colombo"),
    WorldLocation("London, United Kingdom", 51.5074, -0.1278, "Europe/London"),
    WorldLocation("New York, United States", 40.7128, -74.0060, "America/New_York"),
    WorldLocation("Tokyo, Japan", 35.6762, 139.6503, "Asia/Tokyo"),
    WorldLocation("Sydney, Australia", -33.8688, 151.2093, "Australia/Sydney"),
]

# Every country/territory below is listed by name with its capital
# city's coordinates, so typing the COUNTRY name ("Nepal") finds it just
# as well as typing a city name would.
_COUNTRIES: list[WorldLocation] = [
    # -- Africa --------------------------------------------------------
    WorldLocation("Algeria", 36.75, 3.06, "Africa/Algiers"),
    WorldLocation("Angola", -8.84, 13.23, "Africa/Luanda"),
    WorldLocation("Benin", 6.50, 2.60, "Africa/Porto-Novo"),
    WorldLocation("Botswana", -24.65, 25.91, "Africa/Gaborone"),
    WorldLocation("Burkina Faso", 12.37, -1.53, "Africa/Ouagadougou"),
    WorldLocation("Burundi", -3.43, 29.93, "Africa/Bujumbura"),
    WorldLocation("Cabo Verde", 14.93, -23.51, "Atlantic/Cape_Verde"),
    WorldLocation("Cameroon", 3.87, 11.52, "Africa/Douala"),
    WorldLocation("Central African Republic", 4.37, 18.56, "Africa/Bangui"),
    WorldLocation("Chad", 12.13, 15.06, "Africa/Ndjamena"),
    WorldLocation("Comoros", -11.70, 43.26, "Indian/Comoro"),
    WorldLocation("Congo (Republic of the)", -4.27, 15.28, "Africa/Brazzaville"),
    WorldLocation("Congo (Democratic Republic)", -4.44, 15.27, "Africa/Kinshasa"),
    WorldLocation("Djibouti", 11.59, 43.15, "Africa/Djibouti"),
    WorldLocation("Egypt", 30.04, 31.24, "Africa/Cairo"),
    WorldLocation("Equatorial Guinea", 3.75, 8.78, "Africa/Malabo"),
    WorldLocation("Eritrea", 15.32, 38.93, "Africa/Asmara"),
    WorldLocation("Eswatini", -26.32, 31.13, "Africa/Mbabane"),
    WorldLocation("Ethiopia", 9.03, 38.74, "Africa/Addis_Ababa"),
    WorldLocation("Gabon", 0.42, 9.45, "Africa/Libreville"),
    WorldLocation("Gambia", 13.45, -16.58, "Africa/Banjul"),
    WorldLocation("Ghana", 5.60, -0.19, "Africa/Accra"),
    WorldLocation("Guinea", 9.64, -13.58, "Africa/Conakry"),
    WorldLocation("Guinea-Bissau", 11.86, -15.60, "Africa/Bissau"),
    WorldLocation("Ivory Coast", 6.82, -5.28, "Africa/Abidjan"),
    WorldLocation("Kenya", -1.29, 36.82, "Africa/Nairobi"),
    WorldLocation("Lesotho", -29.31, 27.48, "Africa/Maseru"),
    WorldLocation("Liberia", 6.30, -10.80, "Africa/Monrovia"),
    WorldLocation("Libya", 32.89, 13.19, "Africa/Tripoli"),
    WorldLocation("Madagascar", -18.88, 47.51, "Indian/Antananarivo"),
    WorldLocation("Malawi", -13.96, 33.79, "Africa/Blantyre"),
    WorldLocation("Mali", 12.65, -8.00, "Africa/Bamako"),
    WorldLocation("Mauritania", 18.09, -15.98, "Africa/Nouakchott"),
    WorldLocation("Mauritius", -20.16, 57.50, "Indian/Mauritius"),
    WorldLocation("Morocco", 34.02, -6.83, "Africa/Casablanca"),
    WorldLocation("Mozambique", -25.97, 32.57, "Africa/Maputo"),
    WorldLocation("Namibia", -22.56, 17.08, "Africa/Windhoek"),
    WorldLocation("Niger", 13.51, 2.11, "Africa/Niamey"),
    WorldLocation("Nigeria", 9.08, 7.40, "Africa/Lagos"),
    WorldLocation("Rwanda", -1.94, 30.06, "Africa/Kigali"),
    WorldLocation("Sao Tome and Principe", 0.34, 6.73, "Africa/Sao_Tome"),
    WorldLocation("Senegal", 14.72, -17.47, "Africa/Dakar"),
    WorldLocation("Seychelles", -4.62, 55.45, "Indian/Mahe"),
    WorldLocation("Sierra Leone", 8.48, -13.23, "Africa/Freetown"),
    WorldLocation("Somalia", 2.04, 45.34, "Africa/Mogadishu"),
    WorldLocation("South Africa", -25.75, 28.19, "Africa/Johannesburg"),
    WorldLocation("South Sudan", 4.85, 31.58, "Africa/Juba"),
    WorldLocation("Sudan", 15.50, 32.56, "Africa/Khartoum"),
    WorldLocation("Tanzania", -6.16, 35.75, "Africa/Dar_es_Salaam"),
    WorldLocation("Togo", 6.13, 1.22, "Africa/Lome"),
    WorldLocation("Tunisia", 36.81, 10.18, "Africa/Tunis"),
    WorldLocation("Uganda", 0.35, 32.58, "Africa/Kampala"),
    WorldLocation("Zambia", -15.39, 28.32, "Africa/Lusaka"),
    WorldLocation("Zimbabwe", -17.83, 31.05, "Africa/Harare"),
    # -- Americas --------------------------------------------------------
    WorldLocation("Antigua and Barbuda", 17.12, -61.85, "America/Antigua"),
    WorldLocation("Argentina", -34.60, -58.38, "America/Argentina/Buenos_Aires"),
    WorldLocation("Bahamas", 25.05, -77.36, "America/Nassau"),
    WorldLocation("Barbados", 13.10, -59.62, "America/Barbados"),
    WorldLocation("Belize", 17.25, -88.77, "America/Belize"),
    WorldLocation("Bolivia", -16.50, -68.15, "America/La_Paz"),
    WorldLocation("Brazil", -15.79, -47.88, "America/Sao_Paulo"),
    WorldLocation("Canada", 45.42, -75.70, "America/Toronto"),
    WorldLocation("Chile", -33.45, -70.67, "America/Santiago"),
    WorldLocation("Colombia", 4.71, -74.07, "America/Bogota"),
    WorldLocation("Costa Rica", 9.93, -84.08, "America/Costa_Rica"),
    WorldLocation("Cuba", 23.13, -82.38, "America/Havana"),
    WorldLocation("Dominica", 15.30, -61.39, "America/Dominica"),
    WorldLocation("Dominican Republic", 18.49, -69.93, "America/Santo_Domingo"),
    WorldLocation("Ecuador", -0.23, -78.52, "America/Guayaquil"),
    WorldLocation("El Salvador", 13.69, -89.22, "America/El_Salvador"),
    WorldLocation("Greenland", 64.18, -51.72, "America/Nuuk"),
    WorldLocation("Grenada", 12.05, -61.75, "America/Grenada"),
    WorldLocation("Guatemala", 14.63, -90.51, "America/Guatemala"),
    WorldLocation("Guyana", 6.80, -58.16, "America/Guyana"),
    WorldLocation("Haiti", 18.59, -72.31, "America/Port-au-Prince"),
    WorldLocation("Honduras", 14.07, -87.19, "America/Tegucigalpa"),
    WorldLocation("Jamaica", 17.97, -76.79, "America/Jamaica"),
    WorldLocation("Mexico", 19.43, -99.13, "America/Mexico_City"),
    WorldLocation("Nicaragua", 12.11, -86.24, "America/Managua"),
    WorldLocation("Panama", 8.99, -79.52, "America/Panama"),
    WorldLocation("Paraguay", -25.30, -57.64, "America/Asuncion"),
    WorldLocation("Peru", -12.05, -77.04, "America/Lima"),
    WorldLocation("Puerto Rico", 18.47, -66.11, "America/Puerto_Rico"),
    WorldLocation("Saint Kitts and Nevis", 17.30, -62.72, "America/St_Kitts"),
    WorldLocation("Saint Lucia", 14.01, -60.99, "America/St_Lucia"),
    WorldLocation("Saint Vincent and the Grenadines", 13.16, -61.22, "America/St_Vincent"),
    WorldLocation("Suriname", 5.87, -55.17, "America/Paramaribo"),
    WorldLocation("Trinidad and Tobago", 10.65, -61.52, "America/Port_of_Spain"),
    WorldLocation("United States", 38.90, -77.04, "America/New_York"),
    WorldLocation("Uruguay", -34.90, -56.16, "America/Montevideo"),
    WorldLocation("Venezuela", 10.49, -66.88, "America/Caracas"),
    # -- Asia --------------------------------------------------------
    WorldLocation("Afghanistan", 34.56, 69.21, "Asia/Kabul"),
    WorldLocation("Armenia", 40.18, 44.51, "Asia/Yerevan"),
    WorldLocation("Azerbaijan", 40.41, 49.87, "Asia/Baku"),
    WorldLocation("Bahrain", 26.23, 50.59, "Asia/Bahrain"),
    WorldLocation("Bangladesh", 23.81, 90.41, "Asia/Dhaka"),
    WorldLocation("Bhutan", 27.47, 89.64, "Asia/Thimphu"),
    WorldLocation("Brunei", 4.94, 114.94, "Asia/Brunei"),
    WorldLocation("Cambodia", 11.56, 104.92, "Asia/Phnom_Penh"),
    WorldLocation("China", 39.90, 116.41, "Asia/Shanghai"),
    WorldLocation("Cyprus", 35.19, 33.38, "Asia/Nicosia"),
    WorldLocation("Georgia", 41.72, 44.79, "Asia/Tbilisi"),
    WorldLocation("Hong Kong", 22.32, 114.17, "Asia/Hong_Kong"),
    WorldLocation("India", 28.61, 77.21, "Asia/Kolkata"),
    WorldLocation("Indonesia", -6.21, 106.85, "Asia/Jakarta"),
    WorldLocation("Iran", 35.69, 51.39, "Asia/Tehran"),
    WorldLocation("Iraq", 33.31, 44.36, "Asia/Baghdad"),
    WorldLocation("Israel", 31.77, 35.21, "Asia/Jerusalem"),
    WorldLocation("Japan", 35.68, 139.65, "Asia/Tokyo"),
    WorldLocation("Jordan", 31.95, 35.93, "Asia/Amman"),
    WorldLocation("Kazakhstan", 51.18, 71.45, "Asia/Almaty"),
    WorldLocation("Kuwait", 29.38, 47.99, "Asia/Kuwait"),
    WorldLocation("Kyrgyzstan", 42.87, 74.59, "Asia/Bishkek"),
    WorldLocation("Laos", 17.97, 102.60, "Asia/Vientiane"),
    WorldLocation("Lebanon", 33.89, 35.50, "Asia/Beirut"),
    WorldLocation("Macau", 22.20, 113.55, "Asia/Macau"),
    WorldLocation("Malaysia", 3.14, 101.69, "Asia/Kuala_Lumpur"),
    WorldLocation("Maldives", 4.18, 73.51, "Indian/Maldives"),
    WorldLocation("Mongolia", 47.89, 106.91, "Asia/Ulaanbaatar"),
    WorldLocation("Myanmar", 19.76, 96.08, "Asia/Yangon"),
    WorldLocation("Nepal", 27.72, 85.32, "Asia/Kathmandu"),
    WorldLocation("North Korea", 39.02, 125.75, "Asia/Pyongyang"),
    WorldLocation("Oman", 23.59, 58.38, "Asia/Muscat"),
    WorldLocation("Pakistan", 33.68, 73.05, "Asia/Karachi"),
    WorldLocation("Palestine", 31.90, 35.20, "Asia/Gaza"),
    WorldLocation("Philippines", 14.60, 120.98, "Asia/Manila"),
    WorldLocation("Qatar", 25.29, 51.53, "Asia/Qatar"),
    WorldLocation("Saudi Arabia", 24.71, 46.68, "Asia/Riyadh"),
    WorldLocation("Singapore", 1.35, 103.82, "Asia/Singapore"),
    WorldLocation("South Korea", 37.57, 126.98, "Asia/Seoul"),
    WorldLocation("Sri Lanka", 6.93, 79.86, "Asia/Colombo"),
    WorldLocation("Syria", 33.51, 36.28, "Asia/Damascus"),
    WorldLocation("Taiwan", 25.03, 121.57, "Asia/Taipei"),
    WorldLocation("Tajikistan", 38.56, 68.79, "Asia/Dushanbe"),
    WorldLocation("Thailand", 13.75, 100.50, "Asia/Bangkok"),
    WorldLocation("Timor-Leste", -8.56, 125.57, "Asia/Dili"),
    WorldLocation("Turkey", 39.93, 32.86, "Europe/Istanbul"),
    WorldLocation("Turkmenistan", 37.96, 58.33, "Asia/Ashgabat"),
    WorldLocation("United Arab Emirates", 24.47, 54.37, "Asia/Dubai"),
    WorldLocation("Uzbekistan", 41.30, 69.24, "Asia/Tashkent"),
    WorldLocation("Vietnam", 21.03, 105.85, "Asia/Ho_Chi_Minh"),
    WorldLocation("Yemen", 15.35, 44.21, "Asia/Aden"),
    # -- Europe --------------------------------------------------------
    WorldLocation("Albania", 41.33, 19.82, "Europe/Tirane"),
    WorldLocation("Andorra", 42.51, 1.52, "Europe/Andorra"),
    WorldLocation("Austria", 48.21, 16.37, "Europe/Vienna"),
    WorldLocation("Belarus", 53.90, 27.57, "Europe/Minsk"),
    WorldLocation("Belgium", 50.85, 4.35, "Europe/Brussels"),
    WorldLocation("Bosnia and Herzegovina", 43.86, 18.41, "Europe/Sarajevo"),
    WorldLocation("Bulgaria", 42.70, 23.32, "Europe/Sofia"),
    WorldLocation("Croatia", 45.81, 15.98, "Europe/Zagreb"),
    WorldLocation("Czechia", 50.08, 14.44, "Europe/Prague"),
    WorldLocation("Denmark", 55.68, 12.57, "Europe/Copenhagen"),
    WorldLocation("Estonia", 59.44, 24.75, "Europe/Tallinn"),
    WorldLocation("Finland", 60.17, 24.94, "Europe/Helsinki"),
    WorldLocation("France", 48.86, 2.35, "Europe/Paris"),
    WorldLocation("Germany", 52.52, 13.40, "Europe/Berlin"),
    WorldLocation("Greece", 37.98, 23.73, "Europe/Athens"),
    WorldLocation("Hungary", 47.50, 19.04, "Europe/Budapest"),
    WorldLocation("Iceland", 64.15, -21.94, "Atlantic/Reykjavik"),
    WorldLocation("Ireland", 53.35, -6.26, "Europe/Dublin"),
    WorldLocation("Italy", 41.90, 12.50, "Europe/Rome"),
    WorldLocation("Kosovo", 42.67, 21.17, "Europe/Belgrade"),
    WorldLocation("Latvia", 56.95, 24.11, "Europe/Riga"),
    WorldLocation("Liechtenstein", 47.14, 9.52, "Europe/Vaduz"),
    WorldLocation("Lithuania", 54.69, 25.28, "Europe/Vilnius"),
    WorldLocation("Luxembourg", 49.61, 6.13, "Europe/Luxembourg"),
    WorldLocation("Malta", 35.90, 14.51, "Europe/Malta"),
    WorldLocation("Moldova", 47.01, 28.86, "Europe/Chisinau"),
    WorldLocation("Monaco", 43.73, 7.42, "Europe/Monaco"),
    WorldLocation("Montenegro", 42.44, 19.26, "Europe/Podgorica"),
    WorldLocation("Netherlands", 52.37, 4.90, "Europe/Amsterdam"),
    WorldLocation("North Macedonia", 42.00, 21.43, "Europe/Skopje"),
    WorldLocation("Norway", 59.91, 10.75, "Europe/Oslo"),
    WorldLocation("Poland", 52.23, 21.01, "Europe/Warsaw"),
    WorldLocation("Portugal", 38.72, -9.14, "Europe/Lisbon"),
    WorldLocation("Romania", 44.43, 26.10, "Europe/Bucharest"),
    WorldLocation("Russia", 55.76, 37.62, "Europe/Moscow"),
    WorldLocation("San Marino", 43.94, 12.45, "Europe/San_Marino"),
    WorldLocation("Serbia", 44.79, 20.45, "Europe/Belgrade"),
    WorldLocation("Slovakia", 48.15, 17.11, "Europe/Bratislava"),
    WorldLocation("Slovenia", 46.06, 14.51, "Europe/Ljubljana"),
    WorldLocation("Spain", 40.42, -3.70, "Europe/Madrid"),
    WorldLocation("Sweden", 59.33, 18.06, "Europe/Stockholm"),
    WorldLocation("Switzerland", 46.95, 7.45, "Europe/Zurich"),
    WorldLocation("Ukraine", 50.45, 30.52, "Europe/Kyiv"),
    WorldLocation("United Kingdom", 51.51, -0.13, "Europe/London"),
    WorldLocation("Vatican City", 41.90, 12.45, "Europe/Vatican"),
    # -- Oceania --------------------------------------------------------
    WorldLocation("Australia", -35.28, 149.13, "Australia/Sydney"),
    WorldLocation("Fiji", -18.14, 178.44, "Pacific/Fiji"),
    WorldLocation("Kiribati", 1.45, 173.02, "Pacific/Tarawa"),
    WorldLocation("Marshall Islands", 7.12, 171.38, "Pacific/Majuro"),
    WorldLocation("Micronesia", 6.92, 158.16, "Pacific/Pohnpei"),
    WorldLocation("Nauru", -0.55, 166.92, "Pacific/Nauru"),
    WorldLocation("New Zealand", -41.29, 174.78, "Pacific/Auckland"),
    WorldLocation("Palau", 7.50, 134.62, "Pacific/Palau"),
    WorldLocation("Papua New Guinea", -9.48, 147.15, "Pacific/Port_Moresby"),
    WorldLocation("Samoa", -13.83, -171.76, "Pacific/Apia"),
    WorldLocation("Solomon Islands", -9.43, 159.95, "Pacific/Guadalcanal"),
    WorldLocation("Tonga", -21.14, -175.20, "Pacific/Tongatapu"),
    WorldLocation("Tuvalu", -8.52, 179.20, "Pacific/Funafuti"),
    WorldLocation("Vanuatu", -17.73, 168.32, "Pacific/Efate"),
]

# The full searchable gazetteer: favourites first (so they win ties in a
# sorted-alphabetically UI only if the caller wants that), then every
# country - deduplicated by name just in case a favourite and a country
# entry ever collide.
ALL_LOCATIONS: list[WorldLocation] = sorted(
    {loc.name: loc for loc in (*FAVORITE_LOCATIONS, *_COUNTRIES)}.values(),
    key=lambda loc: loc.name,
)


def find_by_name(name: str) -> WorldLocation | None:
    """Exact (case-insensitive) name lookup - used when the search box's
    completer has matched one specific entry."""
    target = name.strip().casefold()
    for loc in ALL_LOCATIONS:
        if loc.name.casefold() == target:
            return loc
    return None
