import streamlit as st
import akshare as ak
from fundutil import FundList, session, select_fund_filename, title
import joblib
from dtale.views import startup
import pandas as pd
import streamlit.components.v1 as stc

filter_fund_type = ['保本型', '定开债券', '固定收益',
                    '货币型', '理财型', '其他创新', '分级杠杆', '债券型']


def update_fund_list():
    '''更新基金列表'''
    fund_em_fund_name_df = ak.fund_em_fund_name()
    rt_trade_df = ak.fund_em_open_fund_daily()
    rt_trade_df = rt_trade_df.loc[:, ['基金代码', '申购状态']]
    fund_em_fund_name_df = fund_em_fund_name_df.merge(rt_trade_df, how='left', on='基金代码')

    fund_list = []
    for code, pingyin, name, type, pingyinquancheng, trade_status in fund_em_fund_name_df.values.tolist():
        if type not in set(filter_fund_type):
            fund_list.append(FundList(code=code,
                                      name=name,
                                      type=type,
                                      trade_status=trade_status
                                      ))
    session.query(FundList).delete()
    session.commit()
    session.bulk_save_objects(fund_list)
    session.commit()


def config_app():
    '''
    设置fund app界面
    :return:
    '''
    st.header(title)
    st.subheader("编辑基金列表")
    print("***")
    select_fund_set = joblib.load(select_fund_filename)
    fund_list = session.query(FundList).filter(FundList.code.in_(select_fund_set))
    fund_list = [(ele.code, ele.name, ele.type) for ele in fund_list]
    fund_num = len(fund_list)

    count = 0
    for code, name, type in fund_list:
        count += 1
        col1, col2, col3, col4 = st.beta_columns(4)
        with col1:
            st.text(code)
        with col2:
            st.text(name)
        with col3:
            st.text(type)
        with col4:
            command_delete = st.button("删除", key="删除" + str(count))
            if command_delete:
                if fund_num > 1:
                    select_fund_set.remove(code)
                    joblib.dump(select_fund_set, select_fund_filename)
                    st.experimental_rerun()
                else:
                    st.warning("只有最后一个基金了，请添加基金")

    col1, col2 = st.beta_columns(2)
    with col1:
        code = st.text_input("添加基金代码", max_chars=6)

    with col2:
        st.header(" ")
        is_add = st.button("添加")
        if is_add:
            if code not in select_fund_set and len(code) == 6:
                fund_list = session.query(FundList).filter(FundList.code == code)
                fund_list = [ele.code for ele in fund_list]
                print(fund_list)
                if fund_list:
                    select_fund_set.add(code)
                    joblib.dump(select_fund_set, select_fund_filename)
                    st.info("添加基金: {}成功".format(code))
                    st.experimental_rerun()
                else:
                    st.error("添加基金: {}失败".format(code))
            else:
                st.error("基金{}已经存在".format(code))


if __name__ == '__main__':
    update_fund_list()
