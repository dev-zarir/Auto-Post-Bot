from helper import FB_Scrapper, post_fb, check_if_valid, check_acc_ie
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from time import sleep
from threading import Thread
import requests

__version__=3.9

amount_of_post_each_page=5

page_ids=[
	"100064620321323",
	"100083712786515",
	"100082319246979",
	"100057273376837",
	"100077463865033",
	# "109057208214046",
	# "110175880338880",
	# "102260178961056",
	"100047072903106",
]

acc_ie='datr=I-OXY2hRUMNU0E1dAZskV8QM; sb=I-OXY6nujoTuO6pyN4G_171u; m_pixel_ratio=1.84375; fr=0emoGyVJMegntNkin.AWUyCee8uv5hhCFFKlbQ12LyFXE.Bjl-Mj.ut.AAA.0.0.Bjl-OS.AWUhAyo-6ic; c_user=100079084416483; xs=29%3AndYbm8KkI70VWg%3A2%3A1670898578%3A-1%3A7642; m_page_voice=100079084416483; wd=391x752; locale=en_US; fbl_st=100625307%3BT%3A27848309; fbl_cs=AhD%2BBtjEWp4wLlaN5IxgmLxdGGpSV2hSYUxSbUU2SXZLbWMybkl5MTNSdA; fbl_ci=841898967085320; vpd=v1%3B752x391x1.84375'

app=Flask(__name__)
app.config['SECRET_KEY']='uwrguyvw4buteuf4gbyugt'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://otnkpdnm:e33_gRZAfzmXc73KHUG5BWeuEX19smt2@satao.db.elephantsql.com/otnkpdnm'

db=SQLAlchemy(app)

class Posts(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	content=db.Column(db.String(1000), unique=True)

@app.route('/')
def home():
	is_valid=check_if_valid()
	acc_id=check_acc_ie(acc_ie)
	return render_template_string(f"""
<h2>Version: {__version__}</h2>
<h2>Token Valid: {is_valid}</h2>
<h2>Acc Valid: {acc_id=='100075924800901'}</h2>
<h2>Acc Checked ID: {acc_id}</h2>
<h3><a href='/log'>View Log</a></h3>
""")

@app.route('/check/<token>')
def check_tk(token):
	resp=requests.get(f'https://graph.facebook.com/v15.0/debug_token?input_token={token}&access_token={token}')
	try:
		return str(resp.json()['data']['is_valid'])
	except:
		return str(False)

@app.route('/log')
def show_log():
	with open('log.txt', 'r', encoding='utf-8') as log:
		log_text=log.read()
		log.close()
	return render_template_string(log_text.replace('\n','<br>'))

def write_log(msg:str):
	with open('log.txt', 'r', encoding='utf-8') as log:
		old_log=log.read()
		log.close()

	with open('log.txt', 'w', encoding='utf-8') as log:
		log.write(old_log+'\n\n'+msg)
		log.close()

def fetch_post_and_publish():
	try:
		posts=[]
		for page_id in page_ids:
			scrapper=FB_Scrapper(page_id, amount_of_post_each_page, acc_ie)
			posts+=scrapper.posts
		for post in posts:
			try:
				with app.app_context():
					if not Posts.query.filter_by(content=post.content).first():
						db.session.add(Posts(content=post.content))
						db.session.commit()
						fb_resp=post_fb(post.content)
						if not fb_resp:
							write_log('Error at posting on facebook: The function retuned False')
			except Exception as e:
				write_log(f'Error at adding row to database: {str(e)}')
				continue
	except Exception as e:
		write_log(f'Error at Scrapping Post: {str(e)}')
		pass

def check_delete_required():
	try:
		with app.app_context():
			all_posts=Posts.query.all()
			if len(all_posts)>=10000:
				for current_post in all_posts[:-1000]:
					db.session.delete(current_post)
					db.session.commit()
	except Exception as e:
		write_log(f'Error at Deleteing Post: {str(e)}')

def run_schedule():
	sleep(60)
	loop=0
	while True:
		loop+=1
		fetch_post_and_publish()
		if loop % 2 == 0:
			check_delete_required()
		sleep(60*15)

t=Thread(target=run_schedule)
t.setDaemon(True)
t.start()

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(host='0.0.0.0', port=80, debug=False)

