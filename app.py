from flask import Flask # import flask module
from flask import render_template
from flask import request
from flask import make_response
from flask import session
from flask import redirect
from flask import jsonify
from flask import url_for

import pymysql # 모듈 import

app = Flask(__name__) # 초기화
app.secret_key = 'your_secret_key'

#초기화면
@app.route('/')
def rootpage():
	user_id = session.get('user_id')
	if user_id:
		return render_template('mainpage.html', user_id=user_id)
	else:
		return redirect('/login')
	
#login
@app.route('/login', methods=['get', 'post'])
def login():
	#요청방식 ( get/ post)
	method = request.method
	if method == 'GET':
		return render_template('login.html')
	else:
		id = request.form.get('id')
		pw = request.form.get('pw')
		if not id or not pw:  # 아이디 또는 비밀번호가 비어 있는 경우
			return "<script>alert(\'ID나 PW가 입력되지 않았습니다. \');window.history.back();</script>"
		conn = pymysql.connect(
			host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234',
			db='nono', charset='utf8'
		) # 데이터베이스 접속
		cursor = conn.cursor() # 커서 객체 생성
		sql = '''
			SELECT count(id) 
			FROM userdata 
			WHERE userdata.id = %s AND userdata.pw = %s
		'''
		cursor.execute(sql,(id,pw)) # SQL 실행
		row = cursor.fetchone()
		cursor.close() # 커서 객체 종료
		conn.close() # 접속 해제
		count = row[0]
		if count == 0:
			return "<script>alert(\'ID와 PW를 확인하세요\');window.history.back();</script>"	
		else:
			session['user_id'] = id
			return mainpage()
			
#logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # 세션에서 user_id 제거
    return redirect('/login')
	
#회원가입
@app.route('/addmember', methods=['get', 'post'])
def addmember():
	method = request.method
	if method == 'GET':
		return render_template('addmember.html')
	else:		
		id = request.form.get('id')
		pw = request.form.get('pw')
		if not id or not pw:  # 아이디 또는 비밀번호가 비어 있는 경우
			return {'msg': 'ID와 PW를 확인하세요', 'code': 2}
		conn = pymysql.connect(
			host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234',
			db='nono', charset='utf8'
		) # 데이터베이스 접속
		cursor = conn.cursor() # 커서 객체 생성
		sql = '''
			SELECT count(id) 
			FROM userdata 
			WHERE userdata.id = %s
		'''
		cursor.execute(sql,(id,)) # SQL 실행
		row = cursor.fetchone()

		count = row[0]

		if count != 0:
			cursor.close() # 커서 객체 종료
			conn.close() # 접속 해제	
			return {'msg': '중복된ID', 'code': 0}
		else :	
			cursor = conn.cursor()
			sql = '''
				insert into  userdata (id, pw) values (%s,%s)
			'''
			cursor.execute(sql,(id,pw)) # SQL 실행
			conn.commit()
			cursor.close() # 커서 객체 종료
			conn.close() # 접속 해제				
			return {'msg': '회원가입 성공', 'code': 1}
#게임선택 mainpage
@app.route('/mainpage')
def mainpage():
	user_id = session.get('user_id')
	if user_id:
		return render_template('mainpage.html', user_id=user_id)
	else:
		return "You are not logged in <br><a href = '/login'></b>" + \
		"click here to login</b></a>"
#nonogram page 이동
@app.route('/nonogram')
def nonogrampage():
	user_id = session.get('user_id')
	if user_id:
		return render_template('nonogram.html', user_id=user_id)
	else:
		return "You are not logged in <br><a href = '/login'></b>" + \
		"click here to login</b></a>"
#nonogram 랭킹
@app.route('/nonorank')
def rank():
    conn = pymysql.connect(
     			host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234',
				db='nono', charset='utf8'
    )
    cursor = conn.cursor()
    sql = 	'''
			SELECT id, score, stime,
       		RANK() OVER (ORDER BY score DESC, stime ASC) AS `rank`
			FROM nonoscore
			ORDER BY score DESC, stime ASC;
		'''
    cursor.execute(sql) # SQL 실행
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('nonorank.html', data=data)

#nonogram 정답시 score표기 및 해당내용 DB저장
@app.route('/score', methods=['post'])
def score():
	data = request.get_json()
	id = session.get('user_id')
	score = data['score']
	time = data['time']
	conn = pymysql.connect(
     			host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234',
				db='nono', charset='utf8'
    )
	cursor = conn.cursor()
	sql = 	'''
			insert into  nonoscore (nonoscore.id, nonoscore.score, nonoscore.stime) values (%s,%s,%s)
		'''
	cursor.execute(sql,(id,score,time)) # SQL 실행
	conn.commit()	
	cursor.close()
	conn.close()
	return {'result': 'ok'}

#가위바위보 게임페이지 이동
@app.route('/rcpgame')
def rcpgamepage():
	user_id = session.get('user_id')
	if user_id:
		return render_template('rcp.html', user_id=user_id)
	else:
		return "You are not logged in <br><a href = '/login'></b>" + \
		"click here to login</b></a>"
	
# 가위바위보 게임 DB 정리
@app.route('/rcpscore', methods=['post'])
def rcpscore():
    # 데이터 쿼리
   data = request.get_json()
   final_score = data['final_score']
   uid = session.get('user_id')
   print(uid)
   # ID = data['ID']
   conn = pymysql.connect(
			host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234',
			db='nono', charset='utf8'
		)
   cursor = conn.cursor() 
   sql =    '''
         insert into  rcpscore (rcpscore.score, rcpscore.id) 
         VALUES (%s,%s)
      '''
   cursor.execute(sql,(final_score, uid)) # SQL 실행
   conn.commit()
   cursor.close()  
   conn.close()
   return {'result': 'ok'}

#nonogram 랭킹
@app.route('/rcprank')
def rcprank():
    conn = pymysql.connect(
     			host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234',
				db='nono', charset='utf8'
    )
    cursor = conn.cursor()
    sql = 	'''
			SELECT score, id, 
       		RANK() OVER (ORDER BY score DESC) AS `rank`
			FROM rcpscore
			ORDER BY score DESC;
		'''
    cursor.execute(sql) # SQL 실행
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('rcprank.html', data=data)

@app.route('/guestbook')
def post():
	user_id = session.get('user_id')
	if user_id:
		return render_template('guestbook.html', user_id=user_id)
	else:
		return redirect('/login')


@app.route('/nonorank', methods=['GET', 'POST'])
def index():
    conn = pymysql.connect(host='databaseson.cftiyrgdgg3r.ap-northeast-1.rds.amazonaws.com', user='admin', password='qwer1234', db='nono', charset='utf8')

    if request.method == 'POST':
        search_id = request.form['search']
        cursor = conn.cursor()

        search_query_scores = """
            SELECT ID,score, stime,
             (SELECT COUNT(*) FROM nonoscore s WHERE s.score > t.score) + 1 as actual_rank
            FROM nonoscore t
            WHERE ID = %s
	    	ORDER BY SCORE DESC , stime 
            """

        cursor.execute(search_query_scores, (search_id,))
        data_scores = cursor.fetchall()
           
        data = data_scores 

    else:
        cursor = conn.cursor()
        select_query = "SELECT score, id, stime, RANK() OVER (ORDER BY score DESC stime ASC) AS rr FROM nonoscore"
        cursor.execute(select_query)
        data = cursor.fetchall()
        
    cursor.close()
    conn.close()

    return render_template('nonorank.html', data=data)

@app.route('/review', methods=['GET', 'post'])
def review():
	user_id = session.get('user_id')
	return render_template('review.html',user_id=user_id)


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=80) # flask 실행

