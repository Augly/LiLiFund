import pandas as pd
import requests
from fund_utils.fundutil import session, FundHistory, \
    FundList, ShortPurchaseIndex, db, KDJPurchaseIndex, header


class Proxy_pool(object):

    def __init__(self):
        self.inital_url = "https://ip.jiangxianli.com/?page={}&country=%E4%B8%AD%E5%9B%BD"
        self.test_url = "https://fundf10.eastmoney.com/jjfl_000216.html"

    def get_proxy(self):
        count = 1

        # 抓取代理地址
        all_proxy = []
        while count < 100:
            url = self.inital_url.format(count)
            df = pd.read_html(url)[0]
            if df.empty:
                break
            all_proxy.append(df)
            count += 1

        if all_proxy:
            all_proxy = pd.concat(all_proxy)
            return all_proxy
        else:
            return

    def save_proxy(self):

        pass

    def eval_proxy(self):
        '''验证代理可用'''
        all_proxy = self.get_proxy()
        userful_proxy = []
        if isinstance(all_proxy, pd.DataFrame):
            for ip, port, _, proxy_type, location, country, operater, speed, live_time, last_modify, _ in all_proxy.values.tolist():
                proxy_type = 'https' if proxy_type.lower() == 'https' else 'http'
                proxy = {proxy_type: "{}:{}".format(ip, port)}
                if "毫秒" in speed:
                    try:
                        response = requests.get(self.test_url, proxies=proxy)
                        response.raise_for_status()
                        userful_proxy.append([proxy_type, ip, port])
                    except Exception as e:
                        print("{}:{} failed".format(ip, port))
                        import traceback
                        traceback.print_exc()
                        pass
        return userful_proxy


proxy_pool = Proxy_pool()

if __name__ == '__main__':
    proxy_pool.eval_proxy()
