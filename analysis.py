import sys
import sqlite3
import jieba.analyse
from wordcloud import WordCloud
from PIL import Image
import numpy as np
#import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import random
#jieba.load_userdict("namedict.txt")
# 设置相关的文件路径
bg_image_path = "bg.png"
text_path = sys.argv[1]# first argument if input file
font_path = 'font.ttf'
stopwords_path = 'stopwords.txt'

def clean_using_stopword(text):
	"""
	去除停顿词，利用常见停顿词表+自建词库
	:param text:
	:return:
	"""
	mywordlist = []
	seg_list = jieba.cut(text, cut_all=False)
	liststr = "/".join(seg_list)
	with open(stopwords_path) as f_stop:
		f_stop_text = f_stop.read()
		#f_stop_text = unicode(f_stop_text, 'utf-8')
	f_stop_seg_list = f_stop_text.split('\n')
	for myword in liststr.split('/'):  # 去除停顿词，生成新文档
		if not (myword.strip() in f_stop_seg_list) and len(myword.strip()) > 1:
			mywordlist.append(myword)
	return ''.join(mywordlist)

def preprocessing():
	"""
	文本预处理
	:return:
	"""
	with open(text_path) as f:
		content = f.read()
	return clean_using_stopword(content)
	return content

def extract_keywords():
	"""
	利用jieba来进行中文分词。
	analyse.extract_tags采用TF-IDF算法进行关键词的提取。
	:return:
	"""
	# 抽取1000个关键词，带权重，后面需要根据权重来生成词云
	allow_pos = ('nr',)  # 词性
	tags = jieba.analyse.extract_tags(preprocessing(), 2000, withWeight=True)
	keywords = dict()
	conn = sqlite3.connect('WordFrequency.db')
	db = conn.cursor()
	db.execute('''create table if not exists WordFrequency
			(id integer primary key autoincrement,
			word text, 
			frequency float)''')
	for i in tags:
		print("%s\t\t%f" % (i[0], i[1]))
		word = i[0]
		frequency = float(i[1])
		db.execute('''insert into WordFrequency(word, frequency)  values(?,?)''', (word, frequency))
		keywords[i[0]] = i[1]
	conn.commit()
	conn.close()
	return keywords

def draw_wordcloud():
	"""
	生成词云。1.配置WordCloud。2.plt进行显示
	:return:
	"""
	#back_coloring = plt.imread(bg_image_path)  # 设置背景图片
	back_coloring = np.array(Image.open(bg_image_path))
	# 设置词云属性
	wc = WordCloud(font_path=font_path,  # 设置字体
				background_color="white",  # 背景颜色
				max_words=2000,  # 词云显示的最大词数
				max_font_size=180,
				random_state=30,
				mask=back_coloring,  # 设置背景图片
				)
	# 根据频率生成词云
	wc.generate_from_frequencies(extract_keywords())
	# 显示图片
	plt.figure()
	plt.imshow(wc.recolor(color_func=color_setting, random_state=3), interpolation="bilinear")
	plt.axis("off")
	plt.show()
	# 保存到本地
	wc.to_file("wordcloud.jpg")

#hsl(hue, saturation, lightness)
#Hue is a degree on the color wheel from 0 to 360. 0 is red, 120 is green, 240 is blue.
#Saturation is a percentage value; 0% means a shade of gray and 100% is the full color.
#Lightness is also a percentage; 0% is black, 100% is white.
def color_setting(word, font_size, position, orientation, random_state=None, **kwargs):
	return "hsl(15, %d%%, %d%%)" % (random.randint(60, 100), random.randint(0, 70))

if __name__ == '__main__':
	draw_wordcloud()
