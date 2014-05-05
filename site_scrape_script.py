#basic source scraping - MTM

import urllib2
url="http://www.ci.moorhead.mn.us/government/mayor-city-council/council-meetings/council-meeting-archive"
page =urllib2.urlopen(url)
f=page.read()

f.write(data)
