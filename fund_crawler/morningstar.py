from fund_utils.fundutil import logger
import requests
from bs4 import BeautifulSoup
from fund_utils.fundutil import header
import numpy as np
from skimage import io
from tqdm import tqdm
from fund_utils.fundutil import FundRank, session
from fund_utils.fund_config import max_rank_pages


class MorningStart:

    def __init__(self):
        self.url = 'http://cn.morningstar.com/quickrank/default.aspx'
        self.start_array = np.array([0, 42, 84, 126, 168, 210])
        pass

    def get_rating(self):
        res = requests.get(self.url, headers=header)
        html = res.text
        soup = BeautifulSoup(html, 'html5lib')
        view_state = soup.find(id='__VIEWSTATE').get('value')
        VIEWSTATEGENERATOR = soup.find(id='__VIEWSTATEGENERATOR').get('value')
        EVENTVALIDATION = soup.find(id='__EVENTVALIDATION').get('value')
        self.get_table_list(soup)
        session.query(FundRank).delete()
        session.commit()
        for ele in tqdm(range(1, max_rank_pages)):  # 65
            params = {'__EVENTTARGET': "ctl00$cphMain$AspNetPager1",
                      "__EVENTARGUMENT": ele + 1,
                      "__VIEWSTATE": view_state,
                      '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                      '__EVENTVALIDATION': EVENTVALIDATION,
                      'ctl00$cphMain$txtFund': '基金名称',
                      'ctl00$cphMain$ddlPageSite': 25}
            res = requests.post(self.url, headers=header, data=params)
            res.encoding = 'utf-8'
            html = res.text
            soup = BeautifulSoup(html, 'html5lib')
            self.get_table_list(soup)

        # # 生成 dataframe
        # df_rating = pd.DataFrame(data, columns=['code', 'name', 'type', 'star_num'])
        # update_file(df_rating, str(data_dir / 'start_rating'))

    def get_start(self, url):
        array = io.imread(url, as_grey=True)
        star = int(np.abs(self.start_array - (array <= 0.5).sum()).argmin())
        return star

    def get_table_list(self, soup):
        table = soup.find(id="ctl00_cphMain_gridResult")
        trs = list(table.find_all('tr'))[1:]
        for ele in list(trs):
            tds = list(ele.find_all("td"))
            _code = tds[2].find('a').get_text()
            _name = tds[3].find('a').get_text()
            _type = tds[4].get_text()
            three_year = self.get_start(tds[5].find('img').get('src'))
            fund_rank = FundRank(code=_code, name=_name,
                                 type=_type, star_num=three_year)
            session.merge(fund_rank)
            session.commit()
            logger.info(f"finish merge {fund_rank} into db!")


if __name__ == '__main__':
    morning_start = MorningStart()
    morning_start.get_rating()
    pass
