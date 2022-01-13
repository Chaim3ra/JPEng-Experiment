from flask import Flask, render_template, redirect, url_for, request, session
import os
from werkzeug import secure_filename
import random
from sqlalchemy.ext.declarative import declarative_base
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Table, Integer, Text, MetaData, create_engine, ForeignKey

image_folder=os.path.join('static','imageFolder')

app=Flask(__name__,static_url_path = "/static", static_folder = "static")
app.secret_key = "abc"
app.config['images']=image_folder
ImageNumber=0
imagesList=[]
imagesList1=[]
ImageNameList=[]
ImageNameList=os.listdir(os.path.join(app.static_folder, "imageFolder"))
imagesList1 = os.listdir(os.path.join(app.static_folder, "imageFolder"))
SortedNameList=[]
imgcurr=""
currentID=0

ImageNameList.sort()
for i in range(0,len(ImageNameList)):
    SortedNameList.append(os.path.splitext(ImageNameList[i])[0])



tables={}
tablesList=[]
imagenumber=0
name=""
code=""
start=0
sortedImages=[]
end=0
pic=[]
times=[]
currentFilename=""


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="",
    databasename="",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.metadata.clear()

engine = create_engine('sqlite:///:memory:')

Base = declarative_base()
meta = MetaData()



class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.INTEGER, primary_key=True)
    name= db.Column(db.TEXT)
    code = db.Column(db.String(4096))

class results(db.Model):

    __tablename__ = "results"

    id=db.Column(db.INTEGER, primary_key=True)
    user_id = db.Column(db.INTEGER, ForeignKey('users.id'))
    name= db.Column(db.TEXT)
    code = db.Column(db.String(4096))
    total = db.Column(db.TEXT)
    mean = db.Column(db.TEXT)
    buffert = db.Column(db.TEXT)
    fearful = db.Column(db.TEXT)
    hopefuk = db.Column(db.TEXT)
    q1 = db.Column(db.TEXT)
    q2 = db.Column(db.TEXT)
    q3 = db.Column(db.TEXT)
    q4 = db.Column(db.TEXT)
    q5 = db.Column(db.TEXT)


def TableCreator(tablename):
    class imageTable(db.Model):
        __tablename__ = tablename

        id=db.Column(db.INTEGER, primary_key=True)
        user_id=db.Column(db.INTEGER, ForeignKey('users.id'),nullable=False)
        name= db.Column(db.TEXT)
        code = db.Column(db.String(4096))
        choice = db.Column(db.TEXT)
        timetaken = db.Column(db.TEXT)
    return imageTable


images=os.listdir(os.path.join(app.static_folder, "imageFolder"))
for i in images:
    name=str(os.path.splitext(i)[0])
    tables[name]=TableCreator(name)


for i in tables.values():
    i.__table__.create(engine)

def get_images():
    res = random.sample(imagesList1, len(imagesList1))
    return res

def get_resultimage(imgcurr):
    return os.path.join(app.config['images'],imgcurr)

@app.route("/")
def index():
    global ImageNumber,imagesList, sortedImages
    session['imagesList']=get_images()
    session['ImageNumber']=0
    return render_template('index.html')

def returnImage(imagenumber):
	global currentFilename, imagesList
	session['currentFilename']=session['imagesList'][int(imagenumber)]
	currentImage=os.path.join(app.config['images'],session['currentFilename'])
	return currentImage

@app.route('/start',methods=['POST'])
def start_quiz():
    session['attempted']=[]
    global currentID
    session['name'] = request.form['nameField']
    session['code'] = request.form['codeField']
    details=users(name=session['name'],code=session['code'])
    db.session.add(details)
    db.session.commit()
    uq=users.query.filter_by(name=session['name']).first()
    currentID=str(uq.id)
    return redirect('/0')

@app.route('/<imagenumber>')
def show_image(imagenumber):
    session['attempted'].append(imagenumber)
    session['start']=time.time()
    session['end']=time.time()
    while(session['ImageNumber']<len(session['imagesList'])):
        imagenumber=int(imagenumber)
        session['ImageNumber']=imagenumber+1
        session['currentImage']=returnImage(imagenumber)
        session['start'] = time.time()
        return render_template('quiz.html',quiz_image=session['currentImage'],name=session['name'])
    else:
        session['end']=time.time()
        return redirect('/finish')


@app.route('/finish')
def finish_quiz():
    return render_template('feedback.html')


@app.route('/end',methods=['POST'])
def end_quiz():
    session['timeslist']=[]
    session['buffer']=[]
    session['hopeful']=[]
    session['fearful']=[]
    session['mean']=0
    session['total']=0
    bcount=fcount=hcount=0
    session['q1']=request.form['q1']
    session['q2']=request.form['q2']
    session['q3']=request.form['q3']
    session['q4']=request.form['q4']
    session['q5']=request.form['q5']
    for i in session['imagesList']:
        currentImgname=os.path.splitext(i)[0]
        currentImgtable=tables[os.path.splitext(i)[0]]
        timeq=db.session.query(currentImgtable.timetaken).filter(currentImgtable.user_id == currentID).all()
        for row in timeq:
            if row[0] is None:
                row[0]=="0"
            if(str(currentImgname)[0]=='F'):
                session['fearful'].append(float(row[0]))
                fcount=fcount+1
            if(str(currentImgname)[0]=='H'):
                session['hopeful'].append(float(row[0]))
                hcount=hcount+1
            if(str(currentImgname)[0]=='B'):
                session['buffer'].append(float(row[0]))
                bcount=bcount+1
            session['timeslist'].append(float(row[0]))
    session['total']=sum(session['timeslist'])
    session['mean']=(session['total'])/(len(session['attempted']))
    if(bcount==0):
        buffertime=0
    else:
        buffertime=round(sum(session['buffer'])/bcount,3)


    if(fcount==0):
        fearfultime=0
    else:
        fearfultime=round(sum(session['fearful'])/fcount,3)

    if(hcount==0):
        hopefultime=0
    else:
        hopefultime=round(sum(session['hopeful'])/hcount,3)


    details=results(name=session['name'],code=session['code'],total=round(session['total'],3),mean=round(session['mean'],3),hopefuk=hopefultime,fearful=fearfultime,buffert=buffertime,q1=session['q1'],q2=session['q2'],q3=session['q3'],q4=session['q4'],q5=session['q5'])
    db.session.add(details)
    db.session.commit()

    return render_template('end.html',name=session['name'])

@app.route('/share')
def share_image():
    global pic,times,currentFilename
    session['end']=time.time()
    session['timetaken']=session['end']-session['start']
    username = users.query.filter_by(name=session['name']).first()
    ds=tables[os.path.splitext(session['currentFilename'])[0]](name=session['name'],user_id=username.id,code=session['code'],choice="Share",timetaken=round(session['timetaken'],3))
    db.session.add(ds)
    db.session.commit()
    return redirect('/'+str(session['ImageNumber']))

@app.route('/dont_share')
def dont_share_image():
    session['end']=time.time()
    session['timetaken']=session['end']-session['start']
    username = users.query.filter_by(name=session['name']).first()
    ds=tables[os.path.splitext(session['currentFilename'])[0]](name=session['name'],user_id=username.id,code=session['code'],choice="Dont Share",timetaken=round(session['timetaken'],3))
    db.session.add(ds)
    db.session.commit()
    return redirect('/'+str(session['ImageNumber']))


@app.route("/images")
def show_images():
	return str(os.listdir(os.path.join(app.static_folder, "imageFolder")))

@app.route("/sortedimages")
def show_sorted():
	return str(SortedNameList)

@app.route("/Namelist")
def show_names():
	return str(ImageNameList[1])


@app.route('/db/<imagenumber3>')
def db_info(imagenumber3):
    imgcurr=str(ImageNameList[int(imagenumber3)])
    return tables[imgcurr]


@app.route("/pass/results/<imagenumber2>")
def results_table(imagenumber2):
    imagenumber2=int(imagenumber2)
    imgcurr=str(ImageNameList[imagenumber2])
    user_info=tables[SortedNameList[imagenumber2]]
    tabledetails=user_info.query.all()
    resultImage="/static/imageFolder/"+str(imgcurr)
    username = users.query.filter_by(name=session['name']).first()
    return render_template('results.html',user_id=username.id,imgname=SortedNameList[imagenumber2],result_image=resultImage,data=tabledetails)



@app.route("/users")
def show_users():
    userList=results.query.all()
    return render_template("users.html",userinfo=userList)

@app.route("/ids")
def getids():
    global currentID
    list1=[]
    for i in session['imagesList']:
        timeq=db.session.query(tables[os.path.splitext(i)[0]].timetaken).filter(tables[os.path.splitext(i)[0]].user_id == currentID).all()
        for row in timeq:
            list1.append(float(0 if row[0] is None else row[0]))

    return (str(list1)+"|"+str(currentID))







