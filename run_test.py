import pandas as pd
from urlchecker import DataPull, UrlCheck, EmailAlert
import glob
import datetime

def run_check(campaign, path):

    if campaign == "All":
        check = UrlCheck()
        get_data = DataPull(path)
        get_data.run("All")
        file_paths = glob.glob(path +"/*.csv")
        for path in file_paths:
            df = pd.read_csv(path, index_col=0)
            file_name = path.split("/")[-1]
            list_of_urls = list(set(df["FinalURL"]))
            results_dict = check.run(list_of_urls)
            df = check.map_results(results_dict, df)
            df.to_csv(path + "/"+ file_name + ".csv")

        file_paths = glob.glob(path +"/*.csv")
        alert = EmailAlert(['Manoj Dobbali <mdobbali@overstock.com>', "Cory Sakashita <corysakashita@overstock.com>",
                        "Mary Wilcox <mwilcox@overstock.com>","Steven Sun <bsun@overstock.com>"]
                       , file_paths)
        if alert == "on":
            alert.run()
    elif campaign == "site links":
        check = UrlCheck()
        get_data = DataPull(path)
        get_data.run(campaign)
        file_path = path + "/site_links.csv"
        df = pd.read_csv(file_path)
        list_of_urls = list(set(df["FinalURL"]))
        results_dict = check.run(list_of_urls)
        df = check.map_results(results_dict, df)
        df.to_csv(file_path)
        alert = EmailAlert(['Manoj Dobbali <mdobbali@overstock.com>', "Cory Sakashita <corysakashita@overstock.com>",
                        "Mary Wilcox <mwilcox@overstock.com>","Steven Sun <bsun@overstock.com>"]
                       , [file_path])
        if alert == "on":
            alert.run()

    else:
        check = UrlCheck()
        get_data = DataPull(path)
        get_data.run(campaign)
        file_path = path + "/"+campaign +".csv"
        df = pd.read_csv(file_path)
        list_of_urls = list(set(df["FinalURL"]))
        results_dict = check.run(list_of_urls)
        df = check.map_results(results_dict, df)
        df.to_csv(path + "/"+campaign + ".csv")
        file_paths = [file_path]
        alert = EmailAlert(['Manoj Dobbali <mdobbali@overstock.com>', "Cory Sakashita <corysakashita@overstock.com>",
                        "Mary Wilcox <mwilcox@overstock.com>","Steven Sun <bsun@overstock.com>"]
                       , file_paths)
        if alert == "on":
            alert.run()

def run_check_on_files(path):
    df = pd.read_csv(path)
    check = UrlCheck()
    url_list = list(set(df["FinalURL"]))
    results_dict = check.run(url_list)
    df = check.map_results(results_dict, df)
    df.to_csv(path)

if __name__ == "__main__":
    run_check("All", "/Users/")
    alert = "on"
