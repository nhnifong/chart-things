import io
from flask import Flask, send_file, session, request, render_template
import requests
from random import random
import peewee

from scraper import Scraper, float_num_re
from schema import Source, DataEntry, db

db.connect()
db.create_tables([Source, DataEntry])
db.close()


scraper = Scraper()
server = Flask(__name__)

@server.route("/")
def home():
   # Select the top 3 most recently updated data entries 
   lastentry = (DataEntry
      .select(
         DataEntry.source_id.alias('source_id'),
         DataEntry.value.alias('recent_val'),
         DataEntry.last_update.alias('last_update'))
      .order_by(DataEntry.last_update.desc())
      .group_by(DataEntry.source_id)
      .limit(3)
      .alias('last_entry'))
   predicate = (Source.source_id == lastentry.c.source_id)
   query = (Source
      .select(
         Source.source_id.alias('source_id'),
         Source.title.alias('title'),
         (lastentry.c.recent_val).alias('recent_val'),
         (lastentry.c.last_update).alias('last_update'))
      .join(lastentry, on=predicate))

   featured = list(query.dicts()) # calling list forces this generator to be evaluated.

   return render_template('home.html', featured=featured)

@server.route('/screenshot')
def screenshot():
   url = request.args.get('url', '')
   png_data = scraper.get_preview(url)
   return send_file(
      io.BytesIO(png_data),
      attachment_filename='screenshot.png',
      mimetype='image/png'
   )

# called when the screenshot is clicked, causes the element at the clicked location to be identified
# returns inner html content that ends up in the green box.
@server.route('/locate', methods = ['POST'])
def locate():
   url = request.form.get('url', '')
   x = int(request.form.get('x', 0))
   y = int(request.form.get('y', 0))
   allow_id = request.form.get('allow_id', 'true') == 'true'
   selector = scraper.locate_element(url, x, y, allow_id)
   text = scraper.get_text_with_selector(url, selector)
   val = 'Cannot find a number'
   search = float_num_re.search(text)
   if search:
      try:
         val = search.group(0).replace(',', '')
         val = str(float(val))
      except ValueError:
         val = 'Cannot parse as float'
   return render_template('result_inner.html', selector=selector, text=text, val=val, url=url)

@server.route('/track', methods = ['POST'])
def track():
   url = request.form.get('url', '')
   selector = request.form.get('selector', '')
   data_source_name = request.form.get('data_source_name', '')
   data_source_period_hrs = request.form.get('data_source_period_hrs', '')
   period = int(data_source_period_hrs) * 3600
   db.connect()
   sr = Source.create(
      url = url,
      selector = selector,
      period = period,
      title = data_source_name)
   sr.save()
   db.close()
   return """Tracking Started<br>
     <a href="/chart/%i">Chart - %s</a>""" % (sr.source_id, data_source_name)

@server.route('/click')
def click_continue():
   png_data = scraper.click_last_spot()
   print('return screenshot', flush=True)
   return send_file(
      io.BytesIO(png_data),
      attachment_filename='screenshot.png',
      mimetype='image/png'
   )

@server.route('/chart/<source_id>')
def chart(source_id):
   try:
      sid = int(source_id)
   except:
      abort(404)
   db.connect()
   query = (DataEntry
      .select(DataEntry.value, DataEntry.last_update)
      .where(DataEntry.source_id == sid))
   # looks like
   # { x: -10, y: 0 },
   # { x: 0, y: 10 },
   datastring = '\n'.join('{ x: %f, y: %f },' % (item.last_update, item.value) for item in query)
   source = Source.get(Source.source_id == sid)
   db.close()
   return render_template('chart.html', datastring=datastring, title=source.title)

@server.route("/random")
def rzan():
   return "<pre>%0.5f</pre>" % (random())


if __name__ == "__main__":
   server.run(host='0.0.0.0') 