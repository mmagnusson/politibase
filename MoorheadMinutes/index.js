var cheerio = require('cheerio');
var request = require('request');
var moment = require('moment');
var fs = require('fs');
var sleep = require('sleep');


request("http://www.ci.moorhead.mn.us/government/mayor-city-council/council-meetings/council-meeting-archive", function(err, resp, body) {
	if (err)
	    throw err;

	var $ = cheerio.load(body);

	var minuteAnchors = $('tr > td:nth-child(4) > a[href^="http://apps.cityofmoorhead.com/sirepub/view.aspx?CABINET=PUBLISHED_MEETINGS"]');
	
	minuteAnchors.each(function(){
		var link = $(this).attr('href');
		var dateTR = $(this).parents('tr').first().find('td:nth-child(1)');

		var date = moment(dateTR.text());

		if (date.isAfter('2013-01-01')) {
			console.log(date.format('YYYY-MM-DD'));
			request(link).pipe(fs.createWriteStream(date.format('YYYY-MM-DD') + '.pdf'));
			sleep.sleep(7);
		}
	});

});