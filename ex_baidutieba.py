# -*- coding: utf-8 -*-

' 抓取百度贴吧任意贴的爬虫'

__author__ = 'Thomas Wu'

import re
import urllib
import urllib2
import time

'''
 这个用于解决 UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-14: ordinal not in range(128)
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
'''

# 处理页面标签
class Tool(object):
	# 去掉img标签，7位长空格
	removeImage = re.compile('<img.*?>| {7}|')
	# 去掉超链接标签
	removeAddr = re.compile('<a.*?>|</a>')
	# 把换行的标签用 \n替代
	replaceLine = re.compile('<tr>|<div>|</div>|</p>')
	# 把表格制表<td>替换为 \t
	replaceTd = re.compile('<td>')
	# 把段落开头替换为\n加两个空格
	replacePara = re.compile('<p.*?>')
	# 将双换行符或换行符替换为\n
	replaceBR = re.compile('<br><br>|<br>')
	# 将其余标签剔除，因为有该标签，所以前面的标签不必成对的都写
	removeExtraTag = re.compile('<.*?>')
	
	def replace(self, x):
		x = re.sub(self.removeImage,"", x)
		x1 = re.sub(self.removeAddr,"", x)
		x2 = re.sub(self.replaceLine,"\n", x1)
		x3 = re.sub(self.replaceTd, "\t", x2)
		x4 = re.sub(self.replacePara, "\n  ", x3)
		x5 = re.sub(self.replaceBR, "\n", x4)
		x6 = re.sub(self.removeExtraTag, "", x5)
		# strip()用于移除字符串头尾指定的字符（默认为空格）
		return x6.strip()
# 百度贴吧爬虫
class BaiDuTieBa(object):
	# 初始化，传入基地址，及是否只看楼主
	def __init__(self, baseUrl, see_lz, floorTag):
		# 贴吧的基地址
		self.baseURL = baseUrl
		# 是否只看楼主
		self.see_lz = '?see_lz='+ str(see_lz)
		# 传入Tool()类，HTML标签剔除工具类对象
		self.tool = Tool()
		# 全局file变量，文件写入操作对象
		self.file = None
		# 默认的标题，如果没有成功获取到标题，则使用该标题
		self.defaultTitle = u'百度贴吧'
		# 楼层标号 ，初始为1
		self.floor = 1
		# 是否写入楼分隔符的标记
		self.floorTag = floorTag
		
	# 传入某一页的索引，获得页面代码：
	def getPage(self, pageindex):
		try:
			# 构建URL
			url = self.baseURL + self.see_lz +'&pn=' + str(pageindex)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			# print response.read()# 测试用，正式运行可删除。
			# 将页面解码转化为 utf-8编码
			pagecode = response.read().decode('utf-8')
			return pagecode
		except urllib2.URLError,e:
			if hasattr(e, 'reason'):
				print u'连接贴吧失败，原因是：', e.reason
				return None

	# 获取帖子的标题,测试成功！
	def getTitle(self):
		pagecode = self.getPage(1)
		# 标题的正则表达式
		pattern = re.compile('<.*?class="core_title_txt.*?>(.*?)</.*?>',re.S)
		result = re.search(pattern, pagecode)
		if result:
			# 如果存在，则返回标题
			# print result.group(1) # 测试输出
			return result.group(1).strip()
		else:
			return None
			
	# 获取帖子总页数,测试ok!
	def getPageNum(self):
		pagecode = self.getPage(1)  # 每一页的上面显示的总页数都一样，随意取一页都能进行收集总页数
		# 获取帖子总页数的正则表达式
		pattern = re.compile('<li class="l_reply_num".*?</span>.*?<span class="red">(.*?)</span>',re.S)
		result = re.search(pattern, pagecode)
		if result:
			# print result.group(1) # 测试输出
			return result.group(1).strip()
		else:
			return None
	# 获取帖子每一楼的内容：
	def getContent(self,pageindex):
		pagecode = self.getPage(pageindex)
		# 匹配所有的楼层的内容， 获得楼层内容的正则表达式
		pattern = re.compile('<div id="post_content.*?class="d_post_content j_d_post_content.*?>(.*?)</div>',re.S)
		items = re.findall(pattern, pagecode)
		# 试着重新编一个楼层，按照顺序，设置一个变量，每打印出一个结果变量加一，打印出这个变量当做楼层
		# floor = 1 # 测试输出
		contents= []
		for item in items:  # item为(.*?)对应的内容
			# print floor, u'楼' + '-'* 110 + '\n'  # 测试输出
			# print self.tool.replace(item)  # 测试输出
			# floor += 1  #测试输出
			# 将文本进行去除标签处理，同时在前后加入换行符
			content = '\n' + self.tool.replace(item) + '\n'
			contents.append(content.encode('utf-8'))
		return contents
		
	def setFileTitle(self, title):
		# 如果标题不为空，则获取到标题
		if title is not None:
			self.file = open(title + '.txt', "w+")
		else:
			self.file = open(self.defaultTitle + '.txt' + 'w+')

	def closeFile(self):
		self.file.close()
	
	# 向文件写入每一楼的信息
	def writeData(self, contents):
		for item in contents:
			# 判断是否要插入楼层分隔
			if self.floorTag == '1':
				# 楼之间分隔符
				floorLine = '\n' + str(self.floor) + '楼' + '-'* 100 + '\n'
				self.file.write(floorLine)
			self.file.write(item)
			self.floor += 1
	
	def start(self):
		# 获取帖子页数
		pageNum = self.getPageNum()
		# 获取帖子标题
		title = self.getTitle()
		# 设置文件标题
		self.setFileTitle(title)
		if pageNum == None:
			print u"URL已经失效，请重试"
			return
		try:
			print u'该帖子一共有' + str(pageNum) + u"页"
			for i in range(1, int(pageNum)+1):
				print u'正在写入第' + str(i) + u'页数据'
				contents = self.getContent(i)
				self.writeData(contents)
		# 出现异常时
		except IOError, e:
			print u'写入异常，原因' + e.message
		finally:
			print u'写入任务完成!'
			self.closeFile()
		
print u'请输入帖子的代号'
baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
see_lz = raw_input(u"是否只获取楼主发言，若是请输入1，否则输入0\n".encode('gbk'))
floorTag = raw_input(u'是否写入楼层信息，若是请输入1，否则输入0\n'.encode('gbk'))
bdtb = BaiDuTieBa(baseURL, see_lz, floorTag)
bdtb.start()
