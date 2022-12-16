from requests_html import HTMLSession, HTML
from urllib.parse import quote_plus
import requests
import re

acc_tk='EAAMn925dpngBAH1EllZAgG7Sbp6WyjrBjUSpdvbGzMmI06fecV58djkRyvo00f1mWZBqWJVQjLQqBI2rss2P8gKwfdXHYvWRO4Xf5G73IMJmiGUfLujnHG8S9keM3wkjy7SgHEiexwiZBhqCIE5x79gPblePwEQ8HF8Xa5LRIZBUfAwqZAFPn'

# 14 Feb Expire

def check_if_valid():
	resp=requests.get(f'https://graph.facebook.com/v15.0/debug_token?input_token={acc_tk}&access_token={acc_tk}')
	try:
		return resp.json()['data']['is_valid']
	except:
		return False

def post_fb(message):
	resp=requests.post(f"https://graph.facebook.com/v15.0/113023048137080/feed?message={quote_plus(message)}&access_token={acc_tk}")
	if resp.status_code==200:
		return True
	else:
		return False

class FB_Scrapper:
	def __init__(self, page_id:str, post_amount:int, cookie:str):
		self.page_id=page_id
		self.post_amount=post_amount
		self.cookie=convert_to_dict(cookie)
		self.cursor='abcdefg'
		self.session=HTMLSession()
		self.posts=self.get_posts()

	def get_posts(self) -> list:
		posts=[]
		try:
			while True:
				resp=self.send_request()
				self.cursor=resp.search('cursor={}&')[0]
				for article in resp.find('article'):
					if len(article.find('article'))==2:
						if not article.find('article')[1].find('img[alt]') and not article.find('article')[1].find('div[data-ft=\'{"tn":"*s"}\']', first=True).find('a'):
							posts.append(FB_Post(article.find('article')[1]))
					else:
						if not FB_Post(article) in posts:
							if not article.find('img[alt]') and not article.find('div[data-ft=\'{"tn":"*s"}\']', first=True).find('a'):
								posts.append(FB_Post(article))
					if len(posts)>=self.post_amount:
						return posts
		except Exception as e:
			print('Error:', str(e), self.page_id)
			return []

	def send_request(self) -> HTML:
		resp=self.session.get(f'https://mbasic.facebook.com/profile/timeline/stream/?cursor={self.cursor}&profile_id={self.page_id}', cookies=self.cookie)
		return resp.html

class FB_Post:
	def __init__(self, obj):
		self.attr_id=obj.attrs['id']
		self.attr_class=' '.join(obj.attrs['class'])
		self.author=obj.find('h3', first=True).text
		self.content=obj.find('div[data-ft=\'{"tn":"*s"}\']', first=True).text

	def __repr__(self):
		return self.content

	def __eq__(self, other):
		return self.content==other.content

def convert_to_dict(cookie:str) -> dict:
	try:
		fb_cookies=cookie.replace(' ','')
		fb_cookies=fb_cookies.replace('\n','')
		fb_cookies=fb_cookies.split(';')
		if '' in fb_cookies:
			fb_cookies.remove('')
		fb_cookies_dict={}
		for item in fb_cookies:
			name, value=item.split('=')
			fb_cookies_dict[name]=value
		return fb_cookies_dict
	except:
		return False

def check_acc_ie(cookies:str):
	try:
		resp=requests.get('https://mbasic.facebook.com/smshahriar.zarir.94', cookies=convert_to_dict(cookies))
		html=resp.text
		match=re.findall(r'profile_id=\d+', html)
		if not match:
			match=re.findall(r'owner_id=\d+', html)
		if not match:
			match=re.findall(r'confirm/\?bid=\d+', html)
		if not match:
			match=re.findall(r'subscribe.php\?id=\d+', html)
		if not match:
			match=re.findall(r'subject_id=\d+', html)
		if not match:
			match=re.findall(r'poke_target=\d+', html)
		if not match:
			return False
		fb_id=match[0].split('=')[1]
		return fb_id
	except:
		return False