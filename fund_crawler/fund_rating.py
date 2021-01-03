import requests
import re
import pandas as pd
import numpy as np
import arrow
from bs4 import BeautifulSoup
import json
import re
import pandas as pd


class FundRating:
    def __init__(self):
        self._rating_url = 'http://fund.eastmoney.com/data/fundrating.html'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def get_html(self):
        response = requests.get(self._rating_url, headers=self.header)
        html = response.text
        fund_string = re.findall('var fundinfos = "(.*?)"', html)[0].split("|")
        fund_array = []
        num_start = 0
        while num_start < len(fund_string) - 1:
            num_end = num_start + 26
            fund_array.append(
                fund_string[num_start:num_start + 5])
            num_start = num_end
        return fund_array

    def get_fund_list(self):
        # 获取基金排行数据
        fund_array = self.get_html()
        columns = ['code', 'name', 'type', 'person', 'org']
        fund_df = pd.DataFrame(fund_array, columns=columns)

        fund_df['code'] = fund_df['code'].apply(lambda x: x.lstrip("_"))
        return fund_df

    def get_fund_pages(self, params):
        url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
        res = requests.get(url, params=params).text
        soup = BeautifulSoup(res, 'html.parser')
        records = []

        tab = soup.findAll('tbody')[0]
        record = {}
        for tr in tab.findAll('tr'):
            if tr.findAll('td') and len((tr.findAll('td'))) == 7:
                record['Date'] = str(tr.select('td:nth-of-type(1)')[0].getText().strip())
                record['NetAssetValue'] = str(tr.select('td:nth-of-type(3)')[0].getText().strip())
                record['ChangePercent'] = str(tr.select('td:nth-of-type(4)')[0].getText().strip())
                records.append(record.copy())
        return records

    def get_fund_history(self, code, start_date=None):
        try:
            url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
            if not start_date:
                start_date = arrow.now().shift(years=-1).format("YYYY-MM-DD")
            end_date = arrow.now().format("YYYY-MM-DD")
            params = {'type': 'lsjz',
                      'code': code,
                      'page': 1,
                      'per': 65535,
                      'sdate': start_date,
                      'edate': end_date}

            res = requests.get(url, params=params).text
            pages = int(re.findall("pages:(.*),", res)[0])
            records = []

            for ele in range(pages):
                params['page'] = ele
                records.extend(self.get_fund_pages(params))
            records = pd.DataFrame(records)
            records.columns = ['change_percent', 'date', 'net_value']
            records.loc[:, "net_value"] = pd.to_numeric(records.net_value)
            records.dropna(axis=0, inplace=True)
            return records
        except:
            import traceback
            # traceback.print_exc()

    def get_fund_fei_fl(self):
        '''获取基金费率'''
        url = "http://fund.eastmoney.com/feilv.html"
        response = requests.get(url, headers=self.header)
        response.encoding = "gb2312"
        soup = BeautifulSoup(response.text, "lxml")
        all_title_lis = soup.find(id="tbMid").find_all("li", class_="tit")
        all_fl_lis = soup.find(id="tbMid").find_all("li", class_="fl")
        result = []
        for title, fl in zip(all_title_lis, all_fl_lis):
            title_a = title.find_all("a")
            if title_a:
                title_code = title.find_all("a")[0].get_text()
                name = title.find_all("a")[1].get_text()
                txt2 = fl.find("a").find("span", class_="txt2")
                if txt2:
                    fl = txt2.get_text()
                    if fl.strip() == "0.00%" and "债" not in name and "货币" not in name:
                        result.append((title_code, name, fl))
        return result


fund_rate = FundRating()

if __name__ == '__main__':
    records = fund_rate.get_fund_fei_fl()
    print(records)
