# URL Checker

### Intro

AdWords has thousands of ads and each ad has an adcopy with URL.Having that URL pointing to a "0 results page" or "404 Page" will create bad landing page experience and ultimately incerasing the bounce rate. To avoid having such urls in the ads, this utility has been created. This runs every single day across all the campaigns and alerts business with reports on broken URLs.

### Process

This is a three step process:

  - Getting data from Google AdWords API. "PLACEHOLDER_FEED_ITEM_REPORT" and "KEYWORDS_PERFROMANCE_REPORT" have been used to get Final URLs of Sitelinks and ads respectively
  - Checking URL if it is "404 Page" or "0 results" page etc.,
  - Finally, sending business team email alerts about the broken URLs

### Setting Up
If Python is installed follow steps below to run URL-Checker on Adwords URLs. Before running URL-checker,run below command from working directoy to install necessary packages
```sh
$ pip install -r requirements.txt
```
To run url_checker, navigate to current working directory in terminal and run as below:
```sh
$ python run.py
```

If Python is not installed, follow steps below to install before following instructions above
Anaconda Installation : Download Python 3.6
https://www.continuum.io/downloads

> For suggestions or doubts contact:
> Manoj Kumar Dobbali
> (mdobbali@overstock.com)