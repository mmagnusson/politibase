#
import wget
import pdfminer

#This archive site is the one to scrape from for initial parsing of data
#http://www.ci.moorhead.mn.us/government/mayor-city-council/council-meetings/council-meeting-archive

http://www.ci.moorhead.mn.us/government/mayor-city-council/council-meetings/council-meeting-archive

#pull the URL, wildcard?
url = 'http://www.ci.moorhead.mn.us/government/mayor-city-council/council-meetings/council-meeting-archive.html'
#url = 'http://www.futurecrew.com/skaven/song_files/mp3/razorback.mp3'
filename = wget.download(url)

#url breakdown for pdfs
# http://
# apps.cityofmoorhead.com
# /
# sirepub
# /
# cache
# /
# 2
# /
# cdbxyx55mta3objxbrchlh45
# /
# 12638804232014073928257.PDF
