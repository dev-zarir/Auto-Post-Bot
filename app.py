from helper import FB_Scrapper, post_fb, check_if_valid, check_acc_ie
from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
from time import sleep
from threading import Thread

__version__=4.5

amount_of_post_each_page=5

page_ids=[
	"100064620321323",
	"100083712786515",
	"100082319246979",
	"100057273376837",
	"100077463865033",
	"100085399881892",
	"100086212856143",
	# "109057208214046",
	# "110175880338880",
	# "102260178961056",
	"100047072903106",
]

app=Flask(__name__)
app.config['SECRET_KEY']='uwrguyvw4buteuf4gbyugt'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://otnkpdnm:e33_gRZAfzmXc73KHUG5BWeuEX19smt2@satao.db.elephantsql.com/otnkpdnm'

db=SQLAlchemy(app)

class Posts(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	content=db.Column(db.String(1000), unique=True)

class Credentials(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	token=db.Column(db.String(1000))
	cookie=db.Column(db.String(1000))

@app.route('/')
def home():
	is_valid=check_if_valid(get_token())
	acc_id=check_acc_ie(get_cookie())
	return render_template_string(f"""
<h2>Version: {__version__}</h2>
<h2>Token Valid: {is_valid}</h2>
<h2>Acc Valid: {acc_id=='100075924800901'}</h2>
<h2>Acc Checked ID: {acc_id}</h2>
<h3><a href='/log'>View Log</a></h3>
""")

@app.route('/update', methods=['GET', 'POST'])
def update_info():
	if request.method=='POST':
		idb=Credentials.query.get(1)
		token=request.form.get('token')
		cookie=request.form.get('cookie')
		if token!='':
			if not check_if_valid(token):
				return 'Invalid Token'
		if cookie!='':
			if check_acc_ie(cookie)!='100075924800901':
				return 'Invalid Cookie'
		if token and cookie:
			idb.token=token
			idb.cookie=cookie
			db.session.commit()
			return 'Successfully Updated Token and Cookie'
		elif token:
			idb.token=token
			db.session.commit()
			return 'Successfully Updated Token'
		elif cookie:
			idb.cookie=cookie
			db.session.commit()
			return 'Successfully Updated Cookie'
		else:
			return 'Nothing Changed'
	else:
		return render_template_string("""
<form method="POST">
	<label for="token">Your Access Token:</label><br>
	<textarea name="token" id="token"></textarea><br>
	<label for="cookie">Your FB Cookie:</label><br>
	<textarea name="cookie" id="cookie"></textarea><br>
	<input type="submit" name="submit" value="Update">
</form>
""")

@app.route('/log')
def show_log():
	with open('log.txt', 'r', encoding='utf-8') as log:
		log_text=log.read()
		log.close()
	return render_template_string(log_text.replace('\n','<br>'))

def get_token():
	with app.app_context():
		return Credentials.query.get(1).token

def get_cookie():
	with app.app_context():
		return Credentials.query.get(1).cookie

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
			scrapper=FB_Scrapper(page_id, amount_of_post_each_page, get_cookie())
			posts+=scrapper.posts
		for post in posts:
			try:
				with app.app_context():
					if not Posts.query.filter_by(content=post.content).first():
						fb_resp=post_fb(post.content, get_token())
						if not fb_resp:
							write_log('Error at posting on facebook: The function retuned False')
							continue
						db.session.add(Posts(content=post.content))
						db.session.commit()
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

