"""Application-wide constants.

MAX_PAGE_SIZE : int
    Hard upper limit for the ``limit`` query parameter on paginated
    endpoints.  Prevents clients from requesting excessively large pages.

DEFAULT_PAGE_SIZE : int
    Default number of items returned when the client does not specify a
    ``limit`` value.

MAX_DATE_RANGE_DAYS : int
    Maximum span (in days) allowed between ``startBusinessDate`` and
    ``endBusinessDate`` on time-series queries.  Guards against full-table
    scans and excessive memory consumption.
"""

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20
MAX_DATE_RANGE_DAYS = 365
