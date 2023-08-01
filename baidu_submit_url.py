from urllib import error, parse
import urllib.request
import xml.dom.minidom
import json
import ssl

def SSL_ignore():
    """
    description: 忽略局部SSL证书鉴证(不忽略有时会报错)
    :return: object
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def get_requset(content, uri):
    """
    param content : str
    Returns: object
    """
    
    base_url = uri
    
    head = {
        'Content-Type': 'text/plain'
    }
    
    #吧str数据转化为byte字节流的数据
    #content = parse.quote(content)
    #data = bytes(content,'utf-8')
    data = content.encode("utf-8")
    #请求对象的定制
    obj_request = urllib.request.Request(url=base_url,headers=head, data=data, method="POST")#post请求data传参使用Request
    return obj_request

def get_msg(data ,uri, ctx):
    """
    param data: str
    param uri: str
    param ctx: object
    return: dict
    """
    req = get_requset(data, uri)
    con = get_respponse(req, ctx=ctx)
    api_dict = json.loads(con)
    return api_dict

def err_msg(message):
    """
    param message: dict
    return: list
    """
    if message.get('error') is not None:
        print(f'错误原因：{message["error"]}')
        return None
    else:
        reason = []
        keyList = ['not_valid', 'not_same_site']
        for key in keyList:
            if message.get(key) is None:
                continue
            else:
                reason.append(message[key])
                print(f'不合法的url列表：{message[key]}')
                return reason


def get_respponse(obj_request, ctx):
    """
    param obj_request: object
    param ctx: object
    return: str
    """
    try:
        response = urllib.request.urlopen(obj_request, context=ctx, timeout=7.0)
        content = response.read().decode('utf-8')
        return content
    except error.HTTPError as e:  # 子类写上面
        print(f'连接出现了点问题呢,错误代码：{e.getcode()}')
        if e.getcode() == 401:
            print('站点或token错误!')
            erron = {'error':f'{e.reason}'}
            err_msg(erron)
        return json.dumps(erron)
    except error.URLError as e:
        print(f'\nURI错误')
        err_msg({'error':f'{e.reason}'})
        return json.dumps({'error':f'{e.reason}'})
    except Exception as e:
        print(f"响应错误")
        err_msg({'error':f'{e.args}'})
        return json.dumps({'error':f'{e.args}'})

def save_data(ssl, sitemapUrl, remain):
    """_summary_
    param ssl : object
    param sitemapUrl : str
    param remain : int
    Returns: str
    """

    req = urllib.request.Request(
        url=sitemapUrl,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'},
        method="GET"
        )
    content = get_respponse(req, ssl)

    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parseString(content)
    collection = DOMTree.documentElement

    #使用xml模块提供的”getElementsByTagName“接口找到需要的节点
    NodeList = collection.getElementsByTagName("loc")
    strings = 0
    urlList = []

    with open('urls.txt', 'w') as file:

        print('主动推送的链接为：')
        for span in NodeList:
            strings = strings + 1
            url = str(span.childNodes[0].data)#.replace("https://", "https://www.")
            file.write(url + '\n')    
            #新站点一次只能推送一百条
            if(strings < remain + 1):
                urlList.append(url)
                print (f"{strings} : {url}")
        new_url = '\n'.join(urlList)
        file.close()        	

    '''
    with open('urls.txt', 'r') as file:
        content = file.read()
        #print(f'抓取的链接：\n{content}')
    '''
    return new_url


if __name__ == '__main__':
    
    #此处修改为自己的接口调用地址和sitemap站点地图地址
    apiUri = 'http://data.zz.baidu.com/urls?site=https://waahah.xyz&token=JNOTqB3jIKcPu1QP'
    sitemapUrl = 'https://waahah.xyz/sitemap.xml'

    sslContext = SSL_ignore()
    num_msg = get_msg('DailyQuota', apiUri, sslContext)
    try:
        print(f'今日可以推送的URL条数：{num_msg["remain"]}')
        content = save_data(sslContext, sitemapUrl, num_msg["remain"])
        result = get_msg(content, apiUri, sslContext)
        reason = err_msg(result)
        print(f'本次已成功为您推送 {result["success"]} 条')
    except KeyError as e:
        print(f'未获取到返回结果，请检查接口地址是否正确！')
