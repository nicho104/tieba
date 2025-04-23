import requests
from lxml import etree
import time
import re
import json


# 数据采集
class data_spider:
    def __init__(self):
        self.headers = {
            "Host": "tieba.baidu.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            # "Cookie": 'BIDUPSID=24827605FF0E7797A7D46E1DE0369741; PSTM=1672131683; BDUSS=c2amV4N1VTZDVHaENuMWRZeDVoclFWUTFFRlJ6NVEzbmx0LVcwWmFJNm9iQU5rRVFBQUFBJCQAAAAAAAAAAAEAAAA~sS6vU3VubnlNYXJrTGl1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKjf22Oo39tjSV; BDUSS_BFESS=c2amV4N1VTZDVHaENuMWRZeDVoclFWUTFFRlJ6NVEzbmx0LVcwWmFJNm9iQU5rRVFBQUFBJCQAAAAAAAAAAAEAAAA~sS6vU3VubnlNYXJrTGl1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKjf22Oo39tjSV; BAIDUID=67D633B4F1E0BC6C28068EE372637897:SL=0:NR=10:FG=1; STOKEN=6a7784efb7c9ed849c0fc26475ddcb3968b7d225a304d7914126dbe1b2aee9cf; delPer=0; PSINO=2; BAIDUID_BFESS=67D633B4F1E0BC6C28068EE372637897:SL=0:NR=10:FG=1; BDRCVFR[QIvwdWWhfos]=mk3SLVN4HKm; H_PS_PSSID=; BA_HECTOR=21252g002424200ha52h80ma1hv4aen1k; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; ZFY=4WATF57hV9NiFerE1P0Y1S:A5y:ACAPfMgF7Fq:A925cm4:C; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; BDRCVFR[tox4WRQ4-Km]=mk3SLVN4HKm; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1676379744,1676820072; 2939072831_FRSVideoUploadTip=1; video_bubble2939072831=1; USER_JUMP=-1; BAIDU_WISE_UID=wapp_1676820073215_22; arialoadData=false; st_key_id=17; tb_as_data=f7bc6b972fd65c4cfdccb9bffa5f8e95402bc6f2eb93c29aff082fd22abf92cc8038ebef85f3d6318afd8d307b2f62756e08c65b50d2999dc4c6b7d1075f042da9c13f30aefd70766339a0c603e28b42d772fc36f03f749e49bdd4e23000e5767a87cb623ca50693801566a292607409; XFI=c471aec0-b06a-11ed-af15-6301ebeccca1; Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948=1676820813; ab_sr=1.0.1_NmUxZDc4NjVmM2JlNWIyMzUzMGI4ZjBjMDBmYjc0MDhiYmIzYjJiNjEzZDE4YTYxM2M4YzQ1ZWUyZGQ4ZTM5ODcxMTU1MDU1ZWIyMDk0YThkNGVmMDc2YzczMzkwMzkxZWVmMzAwNmJiNWFiYTk3MzQyNzc2ZDY3OGVjM2VhNDQyZGUyMTMzMDExYzk2YmY2MTcxMzljODk4NGVjNDg1NjVhYzJlYWEwZDRhZWRkMmU1MDczNGU4ODVmOWJlZmE3; st_data=be76f5ef46178cf74172c6ba4f6291ce1ee87f6ea06870991dd872a4dbef79747f361ac6f7f78110ad7ad01928d9e88750112909816dcc1097d3219e7a40bde4d7e12ad23f66d1d94f6a588165e3d0e1d16eb5dafe78e8025fdd86a2bb5b5ca8; st_sign=d5070f9e; XFCS=F6D0897EF38DF353B8F6AF9F73CEAB976AFB73ECC1EC0FE1C20E1ECEE247EE4A; XFT=fFl8V1Tnk+08wKT4PLnyrjF9tiAwX0MXsyFaaVMQ23A=; RT="z=1&dm=baidu.com&si=5372d074-60c3-42aa-a5db-751fdde491af&ss=lebjdjoy&sl=j&tt=1nhq&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=fzwo&ul=h5p3"',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        self.tieba_items = []
        self.saver = open('tieba_info.json', 'a+', encoding='utf8')
        self.tieba_name = None

    # 采集百度贴吧的数据
    def spider_tieba(self, tieba_name, base_url):
        # 目标地址
        self.tieba_name = tieba_name
        self.spider_tieba_list(base_url)

    # 时间转换
    def get_time_convert(self, timeStr):
        if (re.match('^\d{1,2}:\d{1,2}$', timeStr) != None):
            day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            timeStr = day + ' ' + timeStr + ':00'
        elif (re.match('^\d{4}-\d{1,2}$', timeStr) != None):
            day = time.strftime('%d', time.localtime(time.time()))
            timeStr = timeStr + '-' + day + ' 00:00:00'
        elif (re.match('^\d{1,2}-\d{1,2}$', timeStr) != None):
            day = time.strftime('%Y', time.localtime(time.time()))
            timeStr = day + '-' + timeStr + ' 00:00:00'
        return timeStr

    # 过滤表情
    def filter_emoji(self, desstr, restr=''):
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    # 采集百度贴吧列表数据
    def spider_tieba_list(self, url):
        print(url)
        time.sleep(2)
        response = requests.get(url, headers=self.headers)
        try:
            response_txt = str(response.content, 'utf-8')
        except Exception as e:
            response_txt = str(response.content, 'gbk')
        # response_txt = str(response.content,'utf-8')
        bs64_str = re.findall(
            '<code class="pagelet_html" id="pagelet_html_frs-list/pagelet/thread_list" style="display:none;">[.\n\S\s]*?</code>',
            response_txt)

        bs64_str = ''.join(bs64_str).replace(
            '<code class="pagelet_html" id="pagelet_html_frs-list/pagelet/thread_list" style="display:none;"><!--', '')
        bs64_str = bs64_str.replace('--></code>', '')
        html = etree.HTML(bs64_str)
        # 标题列表
        title_list = html.xpath('//div[@class="threadlist_title pull_left j_th_tit "]/a[1]/@title')
        # 链接列表
        link_list = html.xpath('//div[@class="threadlist_title pull_left j_th_tit "]/a[1]/@href')
        # 发帖人
        creator_list = html.xpath('//div[@class="threadlist_author pull_right"]/span[@class="tb_icon_author "]/@title')
        # 发帖时间
        create_time_list = html.xpath(
            '//div[@class="threadlist_author pull_right"]/span[@class="pull-right is_show_create_time"]/text()')

        for i in range(len(title_list)):
            item = dict()
            item['create_time'] = create_time_list[i]
            if item['create_time'] == '广告':
                continue
            item['create_time'] = self.get_time_convert(item['create_time'])
            item['title'] = self.filter_emoji(title_list[i])
            item['link'] = 'https://tieba.baidu.com' + link_list[i]
            item['creator'] = self.filter_emoji(creator_list[i]).replace('主题作者: ', '')
            item['content'] = self.filter_emoji(item['title'])
            item['school'] = self.tieba_name
            self.tieba_items.append(item)
        # 保存帖子数据
        self.saver.writelines([json.dumps(item, ensure_ascii=False) + '\n' for item in self.tieba_items])
        self.saver.flush()
        self.tieba_items.clear()

        # 如果有下一页继续采集下一页
        nex_page = html.xpath('//a[@class="next pagination-item "]/@href')
        if len(nex_page) > 0:
            next_url = 'https:' + nex_page[0]

            # 抓取 10000 条数据
            if float(next_url.split('=')[-1]) < 1500:
                try:
                    self.spider_tieba_list(next_url)
                    time.sleep(1)
                except:
                    pass


if __name__ == "__main__":
    data_spider = data_spider()

    school_urls = {
        '中国人民公安大学': 'https://tieba.baidu.com/f?kw=中国人民公安大学&ie=utf-8',
        '中国刑事警察学院': 'https://tieba.baidu.com/f?kw=中国刑事警察学院&ie=utf-8',
        '华北电力大学': 'https://tieba.baidu.com/f?kw=华北电力大学&ie=utf-8',
        '河北大学': 'https://tieba.baidu.com/f?kw=河北大学&ie=utf-8',
        '中央司法警官学院': 'https://tieba.baidu.com/f?kw=中央司法警官学院&ie=utf-8'
    }

    for school in school_urls:
        print("==> 抓取 {} 的贴吧数据".format(school))
        data_spider.spider_tieba(school, school_urls[school])
