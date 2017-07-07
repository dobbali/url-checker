# urlchecker.py: Checks if URL is broken or not
# Manoj Dobbali
# 26/06/2016
"""
Broken URL Checker is a tool to check for URLs which are broken in AdWords Campaigns. Along with all the campaigns, this also checks all the site URLs.
"""

import logging
from googleads import adwords
import time
import urllib.request
from random import randint
import warnings
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
import pandas as pd
from bs4 import BeautifulSoup, Comment
import requests
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

warnings.filterwarnings("ignore")

class DataPull():
    """
    Gets Data from  all the campaigns along with Site links URLS and clean URLs.

    Attributes
    ----------
    report_type : str
        Selection if url checking needs to be done for all the campaigns or all the site links. By default, it is all campaigns.
    """

    def __init__(self):
        """
        Initializing DataPull object.

        Parameters
        ----------
        report_type : str
            Selection if url checking needs to be done for all the campaigns or all the site links. By default, it is all campaigns.

        """

        self.reg_expression = re.compile('\["([\s\S]*)"\]')


    def run(self):
        """
        Preparing data for URL checking process.

        """
        self.all_site_link_pull_data()
        campaign_index = pd.read_csv("data/campaign_index.csv", encoding= "ISO-8859-1")
        self.all_camp_pull_data(campaign_index)
        return 


    def all_site_link_pull_data(self):
        """
        function to pull all site links in adwords
        """
        site_link_report =  {    'reportName': 'PLACEHOLDER_FEED_ITEM_REPORT',
                            'dateRangeType': 'LAST_7_DAYS',
                            'reportType': 'PLACEHOLDER_FEED_ITEM_REPORT',
                            'downloadFormat': 'CSV',
                            'selector': {
                                  'fields': ['FeedItemId','AttributeValues',"CampaignName"],
                                  'predicates': [
                                 #{'field': 'CampaignId', 'operator': 'IN', 'values': [50899044]},
                                 {'field': 'CampaignStatus', 'operator': 'IN', 'values': ['ENABLED']},
                                 {'field': 'PlaceholderType', 'operator': 'IN', 'values':[1]}
                                            ]
                                        }
                             }
        file_path = "data/campaign_reports/site_links.csv"
        df = self.pull_data( file_path, report = site_link_report)
        df = df.reset_index(drop=True)
        df = df.apply(self.url_extract, axis=1)
        df.to_csv(file_path)


    def all_camp_pull_data(self, campaign_index):
        """
        function to pull URL data for all the campaigns. It takes campaign_index dataframe which has name and campaign ID as columns
        """
        final_camp = campaign_index[campaign_index["IO"] == "in"]
        final_camp = final_camp.reset_index(drop=True)
        for index in list(final_camp.index):
            camp_id = final_camp["Campaign ID"].iloc[index]
            camp_name = final_camp["Campaign"].iloc[index]
            file_path = "data/campaign_reports/"+camp_name+".csv"
            df = self.pull_data(file_path, campID=camp_id)
            df = df.rename(index=None, columns={"Final URL": "FinalURL", "Ad group": "AdGroup",
                                                "Custom parameter": "CustomParameter", "Campaign ID": "CampaignID"})
            df = df.reset_index(drop=True)
            df = df.apply(self.url_extract, axis=1)
            df.to_csv(file_path)


    def pull_data(self,filepath, campID = None, report=None,skip_report_header=True, skip_column_header=False, skip_report_summary=True):
        """
        Creating API connection and pulls reports into CSV in data folder in current directory

        Parameters
        ----------
        campID: int
            Campaign ID
        filename : str
            filename is a path where data from API needs to be stored.
        report : json
            report is json formatted report definition for Google AdWords API. When it is none, it takes report definition which pulls data for all campaigns.
        skip_report_header: Boolean
            When skip_report_header is True, data pulled will not have report name. By default it is true.
        skip_column_header: Boolean
            When skip_column_header is True, data pulled will not have column names. By default it is False
        skip_report_summary: Boolean
            When skip_report_summary is True, data pulled will not have summary stats of report in last line. By default it is True

        """
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.transport').setLevel(logging.DEBUG)
        yaml = "/Users/mdobbali/Google Drive/2017/Work/googleads.yaml"
        client = adwords.AdWordsClient.LoadFromStorage(yaml)
        chunk_size = 16 * 1024
        report_downloader = client.GetReportDownloader(version='v201702')

        print("pulling data from API started...")


        # Create report definition.
        if report == None:
            report = {
                  'reportName':'AdGroupReport',
                  'dateRangeType': 'YESTERDAY',
                  'reportType':'KEYWORDS_PERFORMANCE_REPORT',
                  'downloadFormat': 'CSV',
                  'selector': {
                            'fields':['FinalUrls', 'UrlCustomParameters','CampaignName'],
                            'predicates': [{'field': 'CampaignId', 'operator': 'IN', 'values': [campID]},
                                           {'field': 'AdGroupStatus',
                                            'operator': 'IN',
                                            'values': ['ENABLED', 'PAUSED']}
                                ]
                        }
                     }

        stream_data = report_downloader.DownloadReportAsStream(report, skip_report_header=skip_report_header, skip_column_header=skip_column_header,skip_report_summary=skip_report_summary)
        f = open(filepath, 'wb')
        try:

            while True:
                chunk = stream_data.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        finally:
            stream_data.close()
            f.close()

        df = pd.read_csv(filepath)
        df = df.rename(columns={"Attribute Values":"Final URL"})
        df = df[df["Final URL"] != "--"]
        print(df[df["Final URL"] == "--"])
        df = df.rename(index=None, columns={"Final URL": "FinalURL", "Ad group": "AdGroup",
                                           "Custom parameter": "CustomParameter", "Campaign ID": "CampaignID","Campaign":"Identifier"})
        df.to_csv(filepath)
        print("process completed!")

        return df

    def url_extract(self, row):
        """
        An apply function for DataFrame which extracts urls from the report

        Parameters
        ----------
        row : DataFrame

        """
        try:
            row["FinalURL"] = re.findall(self.reg_expression, row["FinalURL"])[0]
        except:
            print(row)
        return row



class UrlCheck():
    """
    Takes list of urls and gives if the url is returning any results or not

    Attributes
    ----------
    report_type : list
        list with urls
    """

    def __init__(self):


        self.USER_AGENT = 'User-agent'
        self.ACCEPT = 'Accept'
        self.ACCEPT_ENCODING = 'Accept-Encoding'
        self.ACCEPT_LANGUAGE = 'Accept-language'
        self.CONNECTION = 'Connection'

        self.CONNECTION_DEFAULT = "keep-alive"
        self.ACCEPT_ENCODING_DEFAULT = "utf-8"
        self.ACCEPT_LANGUAGE_DEFAULT = 'en-us,en;q=0.5'

        self.USER_AGENT_MAC_FIREFOX = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/45.0.2"

        self.HEADER_FIREFOX_MAC = {self.USER_AGENT: self.USER_AGENT_MAC_FIREFOX,
            self.ACCEPT: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                self.ACCEPT_ENCODING: self.ACCEPT_ENCODING_DEFAULT,
                   self.ACCEPT_LANGUAGE: self.ACCEPT_LANGUAGE_DEFAULT,
                        self.CONNECTION: self.CONNECTION_DEFAULT}

        self.HEADER_CHROME_WINDOWS = {self.USER_AGENT: "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            self.ACCEPT: "application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                self.ACCEPT_ENCODING: self.ACCEPT_ENCODING_DEFAULT,
                    self.ACCEPT_LANGUAGE: self.ACCEPT_LANGUAGE_DEFAULT,
                        self.CONNECTION: self.CONNECTION_DEFAULT}

        self.USER_HEADERS = [self.HEADER_FIREFOX_MAC, self.HEADER_CHROME_WINDOWS]


    def map_results(self, result_dict, main_df):
        main_df['Results'] = main_df['FinalURL'].map(result_dict)
        return main_df

    def run(self, url_list):
        """
        Multi processing/Multi threading is carried out

        """

        start = time.ctime()
        print(start)
        pT = ThreadPool(100)
        results = pT.map_async(self.get_request, url_list)
        pT.close()
        pT.join()

        all_req = []
        for i in results.get():
            all_req.append(i)

        pP = Pool(20)
        results = pP.map_async(self.get_count, all_req)
        pP.close()
        pP.join()

        counts = []
        for i in results.get():
            counts.append(i)

        result_df = pd.DataFrame({"FinalURL":url_list,"Results":counts})
        result_dict = dict(zip(result_df.FinalURL, result_df.Results))
        end = time.ctime()
        print(end)
        return  result_dict


    # Random User-Agent string
    def get_random_header(self):
        return self.USER_HEADERS[randint(0,(len(self.USER_HEADERS)-1))]

    # Opener with random header settings
    def get_random_opener(self):
        opener = urllib.request.build_opener()
        randomHeader = self.get_random_header()
        opener.addheaders = [(self.USER_AGENT,randomHeader[self.USER_AGENT]),
                             (self.ACCEPT,randomHeader[self.ACCEPT])
                             ,(self.ACCEPT_ENCODING,randomHeader[self.ACCEPT_ENCODING])
                             , (self.ACCEPT_LANGUAGE, randomHeader[self.ACCEPT_LANGUAGE])
                             ,(self.CONNECTION,randomHeader[self.CONNECTION])
                             ]
        return opener

    def get_request(self, url):
        try:
            resp= requests.get(url, self.get_random_header())
        except Exception as e:
            print(e)
            resp = "failed"
        return resp

    def get_count(self, resp):
        """
        Takes url as input and returns number of results display on the page.

        Parameters
        ----------
        url : str
            url that needs to be checked if working or not
        delay_min : int
            minimum time between consecutive checks
        deplay_max : int
            maximum time between consecutive checks
        """

        # time.sleep(random.uniform(delay_min, delay_max))
        try:
            if resp.status_code == 404:
                count = 0
                return count
            soup = BeautifulSoup(resp.text, 'lxml')
            soup_string = str(soup)
            if 'We’re Sorry.' in soup_string:
                return 0

            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            comments = [item.strip() for item in comments]
            pat = re.compile("product result count: ([0-9]+)")
            new_list = [i for i in comments if pat.match(i)]
            count = re.findall("([0-9]+)", str(new_list))
            count = count[0]
        except Exception as e:
            print(e)
            print(resp)
            count = "re check"
        return  count



class EmailAlert():
    """
    Create Email Alerts

    Attributes
    ----------
    list_of_email_ids : list
        list of sender email addresses
    format: string
        message that need to be sent
    """

    def __init__(self, list_of_email_ids, list_of_files):
        """
        Initializing Email Alert object.
        """
        self.list_of_email_ids = list_of_email_ids
        self.list_of_files = list_of_files

    def run(self):
        summary_tuples_list = []
        for df_path in self.list_of_files:
            df = pd.read_csv(df_path)
            file_name = df_path.split("/")[-1].strip(".csv")
            summary_tuple = self.summarize(df, file_name)
            summary_tuples_list.append(summary_tuple)

        summary = pd.DataFrame.from_records(summary_tuples_list,
                                    columns=["Identifier", "total_urls", "unique_urls", "total_ads_with_broken_urls",
                                                 "unique_broken_urls", "recheck_urls"])

        summary.to_csv("data/summary.csv")
        body = self.compose_body()
        for email_id in self.list_of_email_ids:
            self.email_alert(email_id,["data/summary.csv"], body)

        return



    def summarize(self, df, identifier):
        """
        Takes data frame and returns stats required for email formatting.

        Parameters
        ----------
        df : Data Frame
            Data frame from url checking process that needs to be summarized
        identifier: String
            Name of file to identify the simmary stat
        """
        total_urls  = len(df["FinalURL"])
        unique_urls  = len(set(df["FinalURL"]))
        df.Results = df.Results.astype("str")
        broken_url_df = df[df["Results"] == "0"]
        total_ads_with_broken_urls = broken_url_df.shape[0]
        unique_broken_urls = len(set(list(broken_url_df["FinalURL"])))
        try:
            recheck_urls = len(set(df[df["Results"] =="re check"]["FinalURL"]))
        except:
            recheck_urls = 0
        return (identifier, total_urls, unique_urls, total_ads_with_broken_urls,unique_broken_urls, recheck_urls)

    def compose_body(self):
        """
        combines all the result files, summarizes and composes body of email alert.
        """
        master_df = pd.DataFrame()
        for file in self.list_of_files:
            df = pd.read_csv(file, index_col=0)
            master_df = master_df.append(df, ignore_index=True)
        total_urls = list((master_df["FinalURL"]))
        total_urls_count = len(total_urls)
        unique_urls_count =  len(set(total_urls))
        master_df.Results = master_df.Results.astype("str")
        broken_urls_df = master_df[master_df["Results"] == "0"]
        broken_urls_count = len(list(broken_urls_df["FinalURL"]))
        unique_broken_urls_count = len(set(list(broken_urls_df["FinalURL"])))
        perc_urls_broken = 100 * (unique_broken_urls_count/unique_urls_count)
        perc_ads = 100 * (broken_urls_count/total_urls_count)

        body = "Total URLs All Campaigns: "+ str(total_urls_count)+"\n" \
               "Unique URLs All Campaigns: "+ str(unique_urls_count)+" \n" \
               "Percentage of URLs Broken: "+ str(perc_urls_broken)+ "\n" \
               "Percentage of Ads need URL change: "+str(perc_ads)+"\n" \
               "\n\n" \
               "This is a daily alert set up to identify broken URLs across 23 Campaigns in AdWords. \n" \
               "For any questions, contact Manoj Dobbali(mdobbali@overstock.com)"

        return body


    def email_alert(self, email_id, list_of_summary_files, body):
        """
        Sends email alert to email id
        """

        from_address = 'Broken URL Alerts <url_checker@overstock.com>'
        to_address = email_id

        msg = MIMEMultipart()

        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = "URL Checking Process Performed on: " + time.ctime()


        msg.attach(MIMEText(body, 'plain'))


        #attachment = open("data/report.csv", "rb")

        for file_path in list_of_summary_files:
            attachment = open(file_path, "rb")
            file_name = "Broken_URL_Report.csv"
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
            msg.attach(part)

        server = smtplib.SMTP('outlook.overstock.com')
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
