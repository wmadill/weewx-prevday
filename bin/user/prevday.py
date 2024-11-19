# Copyright 2013-2013 Matthew Wall
# Copyright 2024 Bill Madill but based on search
# list extension in WeeWx 5.1 documentation in the
# Customization Guide: Search Lists

"""weewx module that provides a search list extension

Installation

Put this file in the bin/user directory.


Configuration

There isn't any configuration needed.
"""

### Try commenting each of these out to see what is really used...
import logging

import datetime
import time

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

VERSION = "0.1"

log = logging.getLogger(__name__)

class PrevDayVals(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

        self.formatter = generator.formatter
        self.converter = generator.converter
        self.skin_dict = generator.skin_dict
        sd = generator.config_dict.get('PrevDay', {})
        self.binding = sd.get('data_binding', 'weewxd_binding')

    def version(self):
        return VERSION

    def prevday(self):
        pass

    def prevweek(self):
        self.numdays = 7
        return self.getvals(self.numdays)

    def prevmonth(self):
        pass

    def prevyear(self):
        pass

    def getvals(self):
        # Create a TimespanBinder object for the last seven days. First,
        # calculate the time at midnight, seven days ago. The variable week_dt 
        # will be an instance of datetime.date.
        days_dt = datetime.date.fromtimestamp(self.timespan.stop) \
                  - datetime.timedelta(days=self.numdays)
        # Convert it to unix epoch time:
        days_ts = time.mktime(days_dt.timetuple())
        # Form a TimespanBinder object, using the time span we just
        # calculated:
        return TimespanBinder(TimeSpan(week_ts, self.timespan.stop),
                                         self.db_lookup,
                                         context='week',
                                         data_binding=self.binding,
                                         formatter=self.formatter,
                                         converter=self.converter,
                                         skin_dict=self.skin_dict)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a search list extension with two additions.

        Parameters:
          timespan: An instance of weeutil.weeutil.TimeSpan. This will
                    hold the start and stop times of the domain of
                    valid times.

          db_lookup: This is a function that, given a data binding
                     as its only parameter, will return a database manager
                     object.
        """
        self.timespan = timespan
        self.db_lookup = db_lookup

        return [{'prevdays': self}]

##########FIXME
# what follows is a basic unit test of this module.  to run the test:
#
# cd ~/weewx-data
# PYTHONPATH=bin python bin/user/sysstat.py
#
if __name__ == "__main__":
    from weewx.engine import StdEngine
    import weeutil.logger
    import weewx

    weewx.debug = 1
    weeutil.logger.setup('sysstat')

    config = {
        'Station': {
            'station_type': 'Simulator',
            'altitude': [0, 'foot'],
            'latitude': 0,
            'longitude': 0},
        'Simulator': {
            'driver': 'weewx.drivers.simulator',
            'mode': 'simulator'},
        'SystemStatistics': {
            'data_binding': 'sysstat_binding',
            'process': 'sysstat'},
        'DataBindings': {
            'sysstat_binding': {
                'database': 'sysstat_sqlite',
                'manager': 'weewx.manager.DaySummaryManager',
                'table_name': 'archive',
                'schema': 'user.sysstat.schema'}},
        'Databases': {
            'sysstat_sqlite': {
                'database_name': 'sysstat.sdb',
                'database_type': 'SQLite'}},
        'DatabaseTypes': {
            'SQLite': {
                'driver': 'weedb.sqlite',
                'SQLITE_ROOT': 'archive'}},
        'Engine': {
            'Services': {
                'archive_services': 'user.sysstat.SystemStatistics'}},
    }

    # Logged entries are in syslog. View with journalctl --grep=sysstat

    eng = StdEngine(config)
    svc = SystemStatistics(eng, config)

    nowts = lastts = int(time.time())

    loop = 0
    try:
        while True:
            rec = svc.get_data(nowts, lastts)
            print(rec)
            svc.save_data(rec)
            loop += 1
            if loop >= 3:
                break
            time.sleep(5)
            lastts = nowts
            nowts = int(time.time()+0.5)
    except:
        pass
