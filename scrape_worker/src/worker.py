import peewee
from datetime import datetime, timedelta
import time
import re

from schema import db, Source, DataEntry
from scraper import Scraper, float_num_re

scraper = Scraper()

# Query the database for a record that is overdue for being refreshed,
# mark the record as being worked on (do this atomically)
# pull the URL, read the number, add an entry to the series
# finally, (meaning if you either finished or caught an exception) reset the record's last update time. 

def start():
   while True:
      work()
      time.sleep(600) # work every 10 minutes

def work():
   db.connect()
   print("Check for data", flush=True)

   # select a Source where the newest DataEntry having that source's id is older than that source's update period.

   # Subquery which selects the most recent DataEntry for each source_id
   lastentry = (DataEntry
      .select(DataEntry, peewee.fn.Max(DataEntry.last_update).alias('newest'))
      .group_by(DataEntry.source_id)
      .alias('lastentry'))

   predicate = (Source.source_id == lastentry.c.source_id)

   query = (Source
      .select(Source,
         (lastentry.c.newest).alias('news'),
         (peewee.fn.strftime('%s', datetime.now()) - Source.period).alias('nowp'))
      .join(lastentry, peewee.JOIN.LEFT_OUTER, on=predicate)
      .where(
         (lastentry.c.newest == None) |
         (lastentry.c.newest < (peewee.fn.strftime('%s', datetime.now()) - Source.period))))

   for y in query.dicts():
      print(y, flush=True)
      # Scrape the page and collect the data
      try:
         text = scraper.get_text_with_selector(y['url'], y['selector'])
         m = float_num_re.search(text)
         if m:
            val = m.group(0)
            val = val.replace(',' ,'') # remove commas
            val = float(val)
            data_entry = DataEntry.create(
               source_id = y['source_id'],
               value = val,
               last_update = time.mktime(datetime.now().timetuple())) # hard code for now
            data_entry.save()
         print("Collected %s" % (y['url']), flush=True)
      except Exception as e:
         print(e, flush=True)

   db.close()

def days_ago_unix_ts(days):
   return time.mktime((datetime.now()-timedelta(days=days)).timetuple())

def setup_test_data():
   db.connect()

   sources = [
      # update daily, last update is less than 24 ago, this source will not need update
      ('foo.com', 'div > span', 3600*24,
         [
            (0.4, days_ago_unix_ts(3.5)),
            (1.4, days_ago_unix_ts(2.5)),
            (2.4, days_ago_unix_ts(1.5)),
            (3.4, days_ago_unix_ts(0.5)),
         ]),
      # update every 12 days, last update was 13 days ago, this source needs an update
      ('bar.com', 'div > span', 3600*24*12,
         [
            (100, days_ago_unix_ts(13)),
         ]),
      # update hourly, this source has never been pulled, needs update.
      ('see.net', 'div > span', 3600, []),
   ]
   for url, selector, period, entries in sources:
      s = Source.create(url=url, selector=selector, period=period)
      for value, lu in entries:
         e = DataEntry.create(source_id=s, value=value, last_update=lu)

   db.close()

if __name__ == "__main__":
   db.connect()
   if not Source.table_exists():
      db.create_tables([Source, DataEntry])
   db.close()
   print("started", flush=True)

   time.sleep(6)
   # setup_test_data()
   start()
   #work()