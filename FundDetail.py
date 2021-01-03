import streamlit as st
import xalpha as xa
from fundutil import data_dir, title, select_fund_filename, FundList
import joblib
import arrow
import time
import pandas as pd
import logging
from fundutil import session
from datetime import datetime

logger = logging.getLogger(__name__)
xa.set_backend(backend="csv", path=str(data_dir))


@st.cache
def calculate_quantile(self, fund_day=None, days=60):
    now_time = arrow.now()
    now_time_str = now_time.shift(days=-1).format('YYYY-MM-DD')
    if not fund_day:
        fund_day = now_time_str
    fund_day_arrow = arrow.get(fund_day, 'YYYY-MM-DD')
    before_time = fund_day_arrow.shift(days=-days).format('YYYY-MM-DD')
    fund_code_list = self.fund_rate_df['code'].tolist()
    start_time = time.time()
    all_fund_df = [self.get_fund_df(fund_code) for fund_code in fund_code_list]
    end_time = time.time()
    logger.info(f'use {end_time - start_time} load pickle dataframe')
    start_time = time.time()
    all_fund_df = pd.concat(all_fund_df, axis=0)
    all_fund_df['day'] = all_fund_df['day'].apply(str)
    all_fund_df = all_fund_df.loc[(all_fund_df['day'] >= before_time) & (all_fund_df['day'] <= fund_day)]
    all_fund_df = all_fund_df.merge(self.fund_rate_df, on=['code'])  # 表关联
    all_fund_df['mean'] = all_fund_df.groupby('code')["sum_value"].transform('mean')
    all_fund_df['std'] = all_fund_df.groupby('code')["sum_value"].transform('std')

    # 计算归一化结果
    result = all_fund_df.loc[all_fund_df['day'] == fund_day]
    while result.empty:
        fund_day_arrow = arrow.get(fund_day, 'YYYY-MM-DD')
        fund_day = fund_day_arrow.shift(days=-1).format('YYYY-MM-DD')
        result = all_fund_df.loc[all_fund_df['day'] == fund_day]
    result['standard'] = (result['sum_value'] - result['mean']) / result['std']
    result.drop(['id', 'net_value', 'factor', 'sum_value',
                 'acc_factor', 'refactor_net_value',
                 'status', 'addTime', 'modTime',
                 'person', 'org', 'mean', 'std'],
                axis=1, inplace=True)
    result.sort_values(['standard'], inplace=True)
    end_time = time.time()
    logger.info(f'use {end_time - start_time} calculate standard')
    return result


@st.cache
def cal_rsi_index(date, select_fund_set):
    fund_list = session.query(FundList).filter(FundList.code.in_(select_fund_set))
    fund_rel = pd.DataFrame([(ele.code, ele.name, ele.type) for ele in fund_list],
                            columns=['code', 'name', 'type'])
    # 获取数据
    fund_history = []
    for fund_code in select_fund_set:
        try:
            fund_data = xa.fundinfo(fund_code)
            fund_data.price.reset_index(drop=True, inplace=True)
            fund_data.rsi(30)
            fund_data = fund_data.price
            fund_data.loc[:, "code"] = fund_code
            fund_history.append(fund_data)
        except xa.exceptions.ParserFailure as e:
            continue
    fund_history = pd.concat(fund_history, axis=0)
    fund_history = fund_history.groupby("code").tail(1)
    fund_history.sort_values("RSI30", inplace=True)
    fund_history = fund_history.merge(fund_rel, on="code")
    fund_history = fund_history.loc[:, ['code', 'name', 'type', 'RSI30']]
    return fund_history


def detail_app():
    '''展示基金明细'''
    date_now = datetime.now().strftime("%Y-%m-%d")
    st.header(title)
    st.subheader("基金排行")
    select_fund_set = joblib.load(select_fund_filename)
    fund_history = cal_rsi_index(date_now, select_fund_set)
    st.table(fund_history)
    return fund_history


if __name__ == '__main__':
    detail_app()
