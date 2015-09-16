from google.appengine.api import datastore
from google.appengine.api import datastore_types
query = datastore.Query('Page')
entities = query.Get(1000)
for entity in entities:
	entity['sitemapprio'] = '0.5'
	entity['sitemapfreq'] = 'weekly'
	entity['sitemaprodyti'] = True
	datastore.Put(entity)