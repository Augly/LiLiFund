import streamlit as st
from FundConfig import config_app
from FundDetail import detail_app

class MainApp(object):

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title,
                          "function": func})

    def run(self):
        app = st.sidebar.radio(
            "功能",
            self.apps,
            format_func=lambda app: app["title"]
        )
        app['function']()


app = MainApp()
app.add_app("基金详情", detail_app)
app.add_app("基金配置", config_app)
app.run()
