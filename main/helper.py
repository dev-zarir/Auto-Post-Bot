from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from requests_html import HTMLSession, HTML
from selenium.webdriver.common.by import By
from urllib.parse import quote_plus
from seleniumwire import webdriver
import requests
import re

def post_fb(content, cookie):
	def interceptor(request):
		if 'facebook.com' in request.url:
			request.headers['Cookie'] = cookie

	options=webdriver.FirefoxOptions()
	options.add_argument("--log-level=3")
	options.add_argument("--headless")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("--no-sandbox")

	driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
	driver.set_window_size(400,700)
	driver.request_interceptor = interceptor
	# Open Page
	driver.get('https://facebook.com/113023048137080')
	# Click on "What's on your mind"
	find_until_clicklable(driver, By.XPATH, "//span[contains(text(),\"What's on your mind?\")]").click()
	# Find Input Field
	input=find_until_clicklable(driver, By.CSS_SELECTOR, "div[aria-label=\"What's on your mind?\"]")
	# Click on Input Field
	input.click()
	# Type in Input Field
	action=ActionChains(driver)
	for c in content:
		action.send_keys(c)
		action.perform()
	# Click on Post Button
	find_until_clicklable(driver, By.CSS_SELECTOR, "div[aria-label=Post]").click()

	driver.implicitly_wait(5)
	disappared=False
	
	while not disappared:
		try:
			driver.find_element(By.XPATH, "//*[contains(text(), 'Posting')]")
		except:
			disappared=True

	driver.quit()

def find_until_located(driver,find_by,name,timeout=60):
	return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((find_by, name)))

def find_until_clicklable(driver,find_by,name,timeout=60):
	return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((find_by, name)))

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
