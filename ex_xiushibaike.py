# -*- coding:utf-8 -*-

u'  爬取糗事百科测试  '
__author__ = 'Thomas Wu'
import re
import urllib
import urllib2

#糗事百科爬虫类定义
class QSBK(object):
	
	# 定义一些初始变量：
	def __init__(self):
		self.pageIndex = 1
		self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64)'
		# 初始化 headers
		self.headers = {'User-Agent': self.user_agent} 
		# 存放段子的变量，每一个元素是每一页的段子：
		self.stories = []
		# 存放程序是否继续运行的变量
		self.enable = False
		
	# 传入某一页的索引获得页面代码：
	def getPage(self, pageIndex):
		try:
			url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
			# 构建请求request
			request = urllib2.Request(url, headers = self.headers)
			# 利用urlopen获取网页代码：
			response = urllib2.urlopen(request)
			# 将页面解码转化为 utf-8编码
			pageCode = response.read().decode('utf-8')
			return pageCode
		except urllib2.URLError, e:
			if hasatter(e, 'code'):
				print e.code
			if hasatter(e, 'reason'):
				print u'连接糗事百科失败，错误原因是', e.reason
				return None
	
	# 传入某一页的代码， 返回本页不带图片的段子列表：
	def getPageItems(self, pageIndex):
		pageCode = self.getPage(pageIndex)
		if not pageCode:
			print "页面加载失败....."
			return None
		# 匹配样式： 作者 段子内容 点赞数 评论
		pattern = re.compile('<div.*?author clearfix">.*?<h2>(.*?)</h2>.*?<div class="content">.*?<span>(.*?)</span>.*?</div>(.*?)<div class="stats">.*?class="number">(.*?)</i>.*?<i class="number">(.*?)</i>', re.S)
		items = re.findall(pattern, pageCode)
		# 用来存储每页的段子
		pageStories = []
		# 遍历 正则表达式匹配的内容：
		for item in items:
			# 是否含有图片
			haveImg = re.search('img', item[2])
			# 如果没有图片，则加入到list中
			if not haveImg:
				replaceBR = re.compile('<br/>') # 因为文章内容中的<br/>表示换行
				text = re.sub(replaceBR, "\n", item[1])
				# item[0]段子的作者，item[1]内容，item[3]点赞数，item[4]评论数
				pageStories.append([item[0].strip(), text.strip(), item[3].strip(), item[4].strip()])
		return pageStories
		
	# 加载并提取页面内容。存入列表中
	def loadPage(self):
		# 若当前未看的页数少于2页，则加载新一页
		if self.enable == True:
			if len(self.stories) < 2:
				# 获取新一页：
				pageStories = self.getPageItems(self.pageIndex)
				# 将该页的段子存放在全局list中
				if pageStories:
					self.stories.append(pageStories)
					# 获取完后索引码加1.表示读取下一页
					self.pageIndex += 1
				
	# 调用该方法时，每次回车打印输出一个段子：
	def getOneStory(self, pageStories,page):
		# 遍历每一页的段子
		for story in pageStories:
			# 等待用户输入
			input = raw_input()
			# 每当输入一次回车，判断是否加载到新页面：
			self.loadPage()
			if input == 'Q':
				self.enable = False
				return
			print u'第%d页\t发布人:%s\t段子：%s\n赞：%s\n评论数:%s' %(page, story[0], story[1], story[2],story[3])

	# 开始方法：
	def start(self):
		print u'正在读取糗事百科，按回车查看新段子，Q退出'
		# 使变量为True， 程序能够正常运行
		self.enable = True
		# 先加载一页内容
		self.loadPage()
		# 局部变量，控制读取到第几页
		nowpage = 0
		while self.enable:
			if len(self.stories) > 0:
				# 从全局list中获取一页段子
				pageStories = self.stories[0]
				# 当前读取到的页数加1
				nowpage += 1
				# 删除全局list中的第一个元素，因为已经取出了
				del self.stories[0]
				# 输出该页的段子：
				self.getOneStory(pageStories, nowpage)
				
spider = QSBK()
spider.start()



