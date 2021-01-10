import streamlit as st
import xalpha as xa
import logging
from datetime import datetime
from task import title, data_dir, task

logger = logging.getLogger(__name__)


def detail_app():
    '''展示基金明细'''
    st.header(title)
    st.subheader("基金排行")
    fund_history = task.load(task.FUND_BUY_POINT)
    st.table(fund_history)
    return fund_history


if __name__ == '__main__':
    detail_app()
