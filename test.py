from urlchecker import UrlCheck, DataPull

# url = ["https://www.overstock.com/Bedding-Bath/Pillow-Protectors/On-Sale,/on__sale,/4548/cat.html?"]
#
# check = UrlCheck()
# t = check.run(url)
# print(t)

dp = DataPull()
t = dp.all_site_link_pull_data()