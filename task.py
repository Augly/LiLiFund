import schedule
import pandas as pd
import xalpha as xa
import akshare as ak
from pathlib import Path
import joblib
import datetime
import time
from tqdm import tqdm

home_dir = Path(__file__).parent
data_dir = home_dir / 'data'
select_fund_filename = str(home_dir / "data" / "select_fund_set.pkl")
all_market_fund_info_file = str(home_dir / "data" / "all_market_fund_info_file.pkl")
fund_history_data_file = str(home_dir / "data" / "fund_history_data_file.pkl")
fund_buy_point = str(home_dir / "data" / "fund_buy_point.pkl")
title = "李礼基金投资系统"
rsi_index_file = str(home_dir / "data" / "rsi_index.pkl")
task_pid_filename = str(home_dir / "data" / "task.pid")


class Task(object):
    '''设置数据计算服务
    '''

    def __init__(self):
        self.is_schedule = False  # 是否定时
        # 过滤的基金类型
        self.filter_fund_type = ['保本型', '定开债券', '固定收益',
                                 '货币型', '理财型', '其他创新', '分级杠杆', '债券型']
        # 数据集管理
        self.SELECT_FUND_LIST_CODE_FILE = select_fund_filename
        self.ALL_MARKET_FUND_INFO_FILE = all_market_fund_info_file
        self.FUND_HISTORY_DATA_FILE = fund_history_data_file
        self.FUND_BUY_POINT = fund_buy_point

    def load(self, filename):
        '''加载数据集'''
        return joblib.load(filename)

    def get_fund_list(self):
        '''更新基金列表'''
        fund_em_fund_name_df = ak.fund_em_fund_name()
        rt_trade_df = ak.fund_em_open_fund_daily()
        rt_trade_df = rt_trade_df.loc[:, ['基金代码', '申购状态']]
        fund_em_fund_name_df = fund_em_fund_name_df.merge(rt_trade_df, how='left', on='基金代码')
        fund_em_fund_name_df = fund_em_fund_name_df.loc[~fund_em_fund_name_df["基金代码"].isin(self.filter_fund_type)]
        joblib.dump(fund_em_fund_name_df, self.ALL_MARKET_FUND_INFO_FILE)
        return self

    def get_fund_history(self):
        '''下载历史数据
        '''
        now = datetime.datetime.now()
        fund_day_start = now + datetime.timedelta(days=-60)
        fund_day_start = fund_day_start.strftime('%Y-%m-%d')

        # 获取数据
        fund_history = []
        for fund_code in tqdm(self.load(self.SELECT_FUND_LIST_CODE_FILE)):
            try:
                fund_data = xa.fundinfo(fund_code, fetch=False, save=False)
                fund_data.price.reset_index(drop=True, inplace=True)
                fund_data.rsi(30)
                fund_data = fund_data.price
                fund_data.loc[:, "code"] = fund_code
                fund_data = fund_data.loc[fund_data["date"] >= fund_day_start]
                fund_history.append(fund_data)
            except xa.exceptions.ParserFailure as e:
                continue
        fund_history = pd.concat(fund_history, axis=0)
        joblib.dump(fund_history, self.FUND_HISTORY_DATA_FILE)
        return self

    def get_buy_point(self):
        '''
        运行代码
        '''
        fund_history = self.load(self.FUND_HISTORY_DATA_FILE)

        groups = []
        for name, group in tqdm(fund_history.groupby(["code"], as_index=False)):
            group.sort_values("date", inplace=True)
            group.loc[:, "netvalue"] = (group["netvalue"] - group["netvalue"].shift(periods=1)) / group[
                "netvalue"].shift(
                periods=1)
            group.dropna(axis=0, inplace=True)
            group.loc[:, 'MA3'] = group["netvalue"].rolling(window=3).mean()
            group.sort_values('date', ascending=False, inplace=True)
            down_count = 0
            for ele in group["MA3"]:
                if ele < 0:
                    down_count += 1
                else:
                    break
            groups.append((name, down_count, group.loc[group.index[0], "RSI30"]))
        result = pd.DataFrame(groups, columns=['code', 'down_count', "RSI30"])
        all_fund_info = self.load(self.ALL_MARKET_FUND_INFO_FILE).loc[:, ['基金代码', '基金简称']]
        result.sort_values("down_count", ascending=False, inplace=True)
        result = result.merge(all_fund_info, left_on="code", right_on="基金代码")
        result = result.loc[:, ['code', '基金简称', 'down_count', "RSI30"]]
        result.columns = ['基金代码', '基金名称', '下跌次数', "RSI30"]
        joblib.dump(result, fund_buy_point)
        print("finish calculate down count!")
        return self


task = Task()


def run_task():
    task.get_fund_list().get_fund_history().get_buy_point()


if __name__ == '__main__':
    run_task()
    schedule.every().day.at("07:00").do(run_task)
    while True:
        schedule.run_pending()
        time.sleep(1)
