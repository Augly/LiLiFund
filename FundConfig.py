import streamlit as st
from task import title, task
import joblib


def config_app():
    '''
    设置fund app界面
    :return:
    '''
    st.header(title)
    st.subheader("编辑基金列表")

    # 加载基金列表数据
    select_fund_set = joblib.load(task.SELECT_FUND_LIST_CODE_FILE)
    all_fund_list_df = joblib.load(task.ALL_MARKET_FUND_INFO_FILE)
    all_fund_set = set(all_fund_list_df["基金代码"].tolist())
    fund_list = all_fund_list_df.loc[
        all_fund_list_df["基金代码"].isin(select_fund_set), ['基金代码', '基金简称', '基金类型']].values.tolist()
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
                    joblib.dump(select_fund_set, task.SELECT_FUND_LIST_CODE_FILE)
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
                if code in all_fund_set:
                    select_fund_set.add(code)
                    joblib.dump(select_fund_set, task.SELECT_FUND_LIST_CODE_FILE)
                    st.info("添加基金: {}成功".format(code))
                    st.experimental_rerun()
                else:
                    st.error("添加基金: {}失败".format(code))
            else:
                st.error("基金{}已经存在".format(code))
