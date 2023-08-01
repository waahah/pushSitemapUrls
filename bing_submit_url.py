from urllib import request, error, parse
from bs4 import BeautifulSoup as bs
from warnings import filterwarnings
from json import dumps, loads
import ssl

def requset_post(content, apikey, siteUrl):
    """
    param content : list
    param apikey : str
    param siteUrl : str
    Returns: object
    """
    
    base_url = f'https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlBatch?apikey={apikey}'
    
    head = {
        "Content-Type": "application/json; charset=utf-8",
        "Host": "ssl.bing.com"
    }
    
    dict = {
        "siteUrl": f"{siteUrl}",
        "urlList": content
        }
    #吧dict数据类型转化为json类型的数据
    new_json = dumps(dict)
    data = new_json.encode("utf-8")
    #data = bytes(new_json,'utf-8')
    #请求对象的定制
    obj_request = request.Request(url=base_url,headers=head, data=data, method="POST")#post请求data传参使用Request
    return obj_request

def request_get(uri,headers,method):
    """
    uri: str
    headers: dict
    method: str
    Returns: object
    """
    req = request.Request(
        url= uri,
        headers= headers,
        method= method
        )
    return req

def GetUrlQuota(siteUrl, apikey):
    """
    param apikey : str
    Returns: dict
    """
    data = {
        'url': f'https://ssl.bing.com/webmaster/api.svc/json/GetUrlSubmissionQuota?siteUrl={siteUrl}&apikey={apikey}',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'
            },
        'method': "GET"
    }
    req = request_get(data["url"], data["headers"], data["method"])
    conn = get_respponse(req)
    api_dict = loads(conn)
    num_dict = {
        "DailyQuota": api_dict["d"]["DailyQuota"],
        "MonthlyQuota": api_dict["d"]["MonthlyQuota"]
    }
    return num_dict


def get_respponse(obj_request):
    """
    param obj_request: object
    return: str
    """
    try:
        response = request.urlopen(obj_request,timeout=7.0)
        content = response.read().decode('utf-8')
        return content
    except error.HTTPError as e:  # 子类写上面
        print(f'连接出现了点问题呢,错误代码：{e.getcode()}', f'错误原因：{e.reason}', sep='\n')
        return None
    except error.URLError as e:
        print(f'\n控制台日志：{e.reason}')
        return None
    except TimeoutError as e:
        print(f"响应超时,请重新尝试；{e.winerror}")

def save_data(sitemapUrl, apiNum):
    """
    param sitemapUrl : str
    param apiNum : int
    Returns: list
    """

    #strings = 0
    urlList = []
    data = {
        'url': f"{sitemapUrl}",
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'
            },
        'method': "GET"
    }

    req = request_get( data["url"],data["headers"],data["method"])
    content = get_respponse(req)

    filterwarnings("ignore")
    data_ = bs(content,'lxml')
    filterwarnings('default')

    with open('urls.txt', 'w') as file:

        print('主动推送的链接为：')
        for number,url in enumerate(data_.find_all('loc')):
            #strings = strings + 1
            file.write(url.text + '\n')    
            if( number < apiNum):
                urlList.append(url.string)
                print (f"{number + 1} : {url.string}")
        #new_url = '\n'.join(urlList)
        file.close()        	
    '''
    with open('urls.txt', 'r') as file:
        content = file.read()
        #print(f'抓取的链接：\n{content}')
    '''
    return urlList

if __name__ == '__main__':

    ssl._create_default_https_context = ssl._create_unverified_context
    userData = {
        #此处替换为自己的信息
        'apiKey': '26a3a020ce354de19b7e3686e824eb76',
        'siteUrl': 'https://waahah.xyz',
        'sitemapUrl': 'https://waahah.xyz/sitemap.xml'
    }
    siteUrl = userData['siteUrl']
    apiKey = userData['apiKey']
    num_dict = GetUrlQuota(siteUrl, apiKey)
    start_num = num_dict["DailyQuota"]
    print(f'今日可以推送的URL条数：{start_num}', f'本月可以推送的URL条数：{num_dict["MonthlyQuota"]}', sep='\n')
    content = save_data(userData['sitemapUrl'], start_num)
    request_obj = requset_post(content, apiKey, siteUrl)
    content_obj = get_respponse(request_obj)
    end_num = GetUrlQuota(siteUrl, apiKey)
    print(f'返回的结果：\n{content_obj}')  
    print(f'今日还剩余推送URL条数：{end_num["DailyQuota"]}\n本月还剩余次数推送URL条数：{end_num["MonthlyQuota"]}')
    print(f'本次已成功推送{start_num - end_num["DailyQuota"]}条')
