# -*- coding:utf-8 -*-

' 抓取百度贴吧任意贴的爬虫'

__author__ = 'Thomas Wu'

import urllib
import urllib2
import re
class BaiDuTieBa(object):

	def __init__(self, baseUrl, see_lz):
		# 贴吧的基地址
		self.baseURL = baseUrl
		# 是否只看楼主
		self.see_lz = '?see_lz='+ str(see_lz)
	
	# 传入某一页的索引，获得页面代码：
	def getpage(self, pageindex):
		try:
			url = self.baseURL + self.see_lz +'&pn=' + str(pageindex)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			# print response.read(), 测试用，正式运行可删除。
			# 将页面解码转化为 utf-8编码
			pagecode = response.read().decode('utf-8')
			return pagecode
		except urllib2.URLError,e:
			if hasattr(e, 'reason'):
				print u'连接贴吧失败，原因是：', e.reason


	# 获取帖子的标题,测试成功！
	def getTitle(self):
		pagecode = self.getpage(1)
		pattern = re.compile('<.*?class="core_title_txt.*?>(.*?)</.*?>',re.S)
		result = re.search(pattern, pagecode)
		if result:
			print result.group(1) # 测试输出
			return result.group(1).strip()
		else:
			return None
			
	# 获取帖子总页数,测试ok!
	def getPageNum(self):
		pagecode = self.getpage(1)  # 每一页的上面显示的总页数都一样，随意取一页都能进行收集总页数
		pattern = re.compile('<li class="l_reply_num".*?</span>.*?<span class="red">(.*?)</span>',re.S)
		result = re.search(pattern, pagecode)
		if result:
			print result.group(1) # 测试输出
			return result.group(1).strip()
		else:
			return None
	# 获取帖子每一楼的内容：
	def getContent(self,pageindex):
		pagecode = self.getpage(pageindex)
		pattern = re.compile('<div id="post_content.*?class="d_post_content j_d_post_content.*?">(.*?)</div>',re.S)
		items = re.findall(pattern, pagecode)
		print items[1]
			
		
		
		
baseURL = 'http://tieba.baidu.com/p/4933621547'
bdtb = BaiDuTieBa(baseURL, 1)
bdtb.getPageNum()
bdtb.getContent(1)
