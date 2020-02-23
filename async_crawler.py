import time
import asyncio
import requests
import multiprocessing

"""
经过对比发现，这四种的爬取速度从小到大的顺序为：异步协程 < 异步+多进程 < 多进程 < 同步
如果 url更多， 异步+多线程 速度明显更少，可以根据实际情况 选择 不同的 爬取方式 可以 提高 爬取速度哟 ！！！
"""



urls = [
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16488',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16583',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16380',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16911',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16581',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16674',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16112',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/17343',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16659',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16449',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16650',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16751',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16652',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16853',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16854',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16955',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16156',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16157',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16258',
    'https://aaai.org/ocs/index.php/AAAI/AAAI18/paper/viewPaper/16459'
]


'''
提交请求获取AAAI网页,并解析HTML获取title
'''

#
# # 一、测试普通爬虫程序
# def get_title(url, cnt):
#     response = requests.get(url)  # 提交请求,获取响应内容
#     html = response.content  # 获取网页内容(content返回的是bytes型数据,text()获取的是Unicode型数据)
#     title = etree.HTML(html).xpath('//*[@id="title"]/text()')  # 由xpath解析HTML
#     print('第%d个title:%s' % (cnt, ''.join(title)))
#
#
# if __name__ == '__main__':
#     start1 = time.time()
#     i = 0
#     for url in urls:
#         i = i + 1
#         start = time.time()
#         get_title(url, i)
#         print('第%d个title爬取耗时:%.5f秒' % (i, float(time.time() - start)))
#     print('爬取总耗时:%.5f秒' % float(time.time() - start1))
#



# --------------------------------------------------------------------------------------------


# 二、测试基于协程的异步爬虫程序
sem = asyncio.Semaphore(10) # 信号量，控制协程数，防止爬的过快
async def get_title(url):
    async with sem:
        # async with是异步上下文管理器
        async with aiohttp.ClientSession() as session:  # 获取session
            async with session.get(url) as resp:  # 提出请求
                # html_unicode = await resp.text()
                # html = bytes(bytearray(html_unicode, encoding='utf-8'))
                html = await resp.read() # 可直接获取bytes
                title = etree.HTML(html).xpath('//*[@id="title"]/text()')
                print(''.join(title))

'''
调用方
'''
def main():
    loop = asyncio.get_event_loop()           # 获取事件循环
    tasks = [get_title(url) for url in urls]  # 把所有任务放到一个列表中
    loop.run_until_complete(asyncio.wait(tasks)) # 激活协程

   # loop.close()  # 关闭事件循环

if __name__ == '__main__':
    start = time.time()
    main()  # 调用方
    print('总耗时：%.5f秒' % float(time.time()-start))




# 三、测试基于多进程的分布式爬虫程序
# 下面，我们测试多进程爬虫程序，由于我的电脑CPU是12核，所以这里进程池我就设的12。
def get_title(url, cnt):
    response = requests.get(url)  # 提交请求
    html = response.content  # 获取网页内容
    title = etree.HTML(html).xpath('//*[@id="title"]/text()')  # 由xpath解析HTML
    print('第%d个title:%s' % (cnt, ''.join(title)))


'''
调用方
'''


def main():
    print('当前环境CPU核数是：%d核' % multiprocessing.cpu_count())
    p = Pool(12)  # 进程池
    i = 0
    for url in urls:
        i += 1
        p.apply_async(get_title, args=(url, i))
    p.close()
    p.join()  # 运行完所有子进程才能顺序运行后续程序


if __name__ == '__main__':
    start = time.time()
    main()  # 调用方
    print('总耗时：%.5f秒' % float(time.time() - start)) # 总耗时：2.57408秒

# -------------------------------------------------------------------------------

# 四、测试-异步结合多进程-爬虫程序
# 由于解析HTML也需要消耗一定的时间，而aiohttp和asyncio均未提供相关解析方法。所以可以在请求网页的时使用异步程序，在解析HTML使用多进程，两者配合使用，效率更高哦～！
# 【请求网页】：使用协程。
# 【解析HTML】：使用多进程。
from multiprocessing import Pool
import time
from lxml import etree
import aiohttp
import asyncio

htmls = []
titles = []
sem = asyncio.Semaphore(10) # 信号量，控制协程数，防止爬的过快
'''
提交请求获取AAAI网页html
'''
async def get_html(url):
    async with sem:
        # async with是异步上下文管理器
        async with aiohttp.ClientSession() as session:  # 获取session
            async with session.request('GET', url) as resp:  # 提出请求
                html = await resp.read() # 直接获取到bytes
                htmls.append(html)
                print('异步获取%s下的html.' % url)

'''
协程调用方，请求网页
'''
def main_get_html():
    loop = asyncio.get_event_loop()           # 获取事件循环
    tasks = [get_html(url) for url in urls]  # 把所有任务放到一个列表中
    loop.run_until_complete(asyncio.wait(tasks)) # 激活协程
    #loop.close()  # 关闭事件循环
'''
使用多进程解析html
'''
def multi_parse_html(html,cnt):
    title = etree.HTML(html).xpath('//*[@id="title"]/text()')
    titles.append(''.join(title))
    print('第%d个html完成解析－title:%s' % (cnt,''.join(title)))
'''
多进程调用总函数，解析html
'''
def main_parse_html():
    p = Pool(6)
    i = 0
    for html in htmls:
        i += 1
        p.apply_async(multi_parse_html,args=(html,i))
    p.close()
    p.join()


if __name__ == '__main__':
    start = time.time()
    main_get_html()   # 调用方
    main_parse_html() # 解析html
    print('总耗时：%.5f秒' % float(time.time()-start))
