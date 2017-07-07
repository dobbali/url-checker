import pandas as pd
from urlchecker import DataPull, UrlCheck, EmailAlert
import glob

def main():
    get_data = DataPull()
    get_data.run()

    check = UrlCheck()

    file_paths = glob.glob("data/campaign_reports/*.csv")
    for path in file_paths:
        print(path)
        df = pd.read_csv(path, index_col = 0)
        file_name = path.split("/")[-1]
        list_of_urls = list(set(df["FinalURL"]))
        results_dict = check.run(list_of_urls)
        df = check.map_results(results_dict, df)
        df.to_csv("data/results/"+file_name)


    file_paths = glob.glob("data/results/*.csv")
    alert = EmailAlert(['Manoj Dobbali <mdobbali@overstock.com>',"Cory Sakashita <corysakashita@overstock.com>","Mary Wilcox <mwilcox@overstock.com>"]
                       ,file_paths)
    alert.run()


if __name__ == "__main__":
    main()
