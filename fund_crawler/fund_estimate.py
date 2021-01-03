import requests
import datetime
from fund_utils import fundutil
from loguru import logger
import retrying
import json
from tqdm import tqdm

import pandas as pd


class RealTimeFundData:
    def __init__(self):
        pass

    @retrying.retry(stop_max_attempt_number=3)
    def get_fund_estimate(self, fund_code):
        try:
            url = f'http://fundgz.1234567.com.cn/js/{fund_code}.js'
            now = int(datetime.datetime.now().timestamp() * 1000)
            logger.info(f"get estimate for {fund_code} real time timestamp is {now}")
            params = {"rt": now}
            data = requests.get(url, params=params,
                                headers=fundutil.header).text
            #
            # fundcode name     jzrq       dwjz     gsz      gszzl   gztime
            #  基金代码 基金名称   上一天时间  单位净值   估值净值  估计涨幅  估值时间
            json_data = json.loads(data.lstrip("jsonpgz(").rstrip(");"))
            return json_data
        except:
            return {"fundcode": fund_code,
                    "name": None,
                    "jzrq": None,
                    "dwjz": None,
                    "gsz": None,
                    "gszzl": None,
                    "gztime": None}

        # 'jsonpgz({"fundcode":"001186","name":"富国文体健康股票","jzrq":"2020-01-02","dwjz":"1.2390","gsz":"1.2409","gszzl":"0.15","gztime":"2020-01-03 15:00"});'

    def get_estimate_df(self, fund_code_list):
        '''获取基金估值'''
        estimate_df = []
        logger.info("get fund estimate value progress as flow!")
        for ele in tqdm(fund_code_list):
            estimate_df.append(self.get_fund_estimate(ele))
        estimate_df = pd.DataFrame(estimate_df)
        estimate_df.loc[:, 'gsz'] = pd.to_numeric(estimate_df["gsz"])
        current_date = estimate_df.loc[estimate_df["gztime"] != None].loc[0, 'gztime'][:10]
        estimate_df.drop(['name', 'jzrq', 'dwjz', 'gztime', 'gsz'], axis=1, inplace=True)
        estimate_df.rename(columns={"fundcode": "code"}, inplace=True)
        estimate_df['current_date'] = current_date
        return estimate_df


realtime_fund_data = RealTimeFundData()

if __name__ == '__main__':
    json_data = realtime_fund_data.get_estimate_df(['001632'])
    print(json_data)
