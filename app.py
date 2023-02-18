import os
import matplotlib.pyplot as plt
from flask import Flask, request,render_template, jsonify
from scipy.io.wavfile import write
import librosa as lr 
from werkzeug.utils import secure_filename
import joblib
import numpy as np
import python_speech_features as mfcc
from sklearn import preprocessing
import pandas as pd
import plotly.express as px




app = Flask(__name__)

# UPLOAD_FOLDER = 'static/file/'
app.secret_key = "cairocoders-ednalan"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# plotting features

def plotFeature(x ,y):

    DataTowCo = pd.read_csv("DataFile.csv")
    amira= DataTowCo.iloc[:, 0]
    ezzat=DataTowCo.iloc[:, 1]
    mar=DataTowCo.iloc[:, 2]
    osama=DataTowCo.iloc[:,3]
    amiraRang=np.linspace(-.3, .3, num=len(amira))
    ezzatRange=np.linspace(.7, 1.3 ,num=len(ezzat))
    marRange=np.linspace( 1.7,2.3 ,num=len(mar))
    osamaRange=np.linspace(2.7 ,3.3  ,num=len(osama))
    plt.figure(figsize=(14, 5))
    plt.plot(amiraRang ,amira , 'yo',label="amira")
    plt.plot(ezzatRange ,ezzat , 'ro',label="ezzat")
    plt.plot(marRange ,mar , 'go',label="mariam")
    plt.plot(osamaRange ,osama , 'bo',label="osama")
    plt.plot(x,y ,'k*' ,markersize=30)
    plt.legend(loc="lower left")
    plt.xlabel("clusters")
    plt.ylabel("similarity score")
    plt.grid()

    # plt.legend(["yellow","amira"],["red","ezzat"],["green","mariam"],["blue","osama"])
    plt.savefig("static\images\hoold.png")
    


# extracting features from audio recorded


def calculate_delta(array):
   
    rows, cols = array.shape
    # print(rows)
    # print(cols)
    deltas = np.zeros((rows,20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first =0
            else:
                first = i-j
            if i+j > rows-1:
                second = rows-1
            else:
                second = i+j 
            index.append((second,first))
            j+=1
        deltas[i] = ( array[index[0][0]]-array[index[0][1]] + (2 * (array[index[1][0]]-array[index[1][1]])) ) / 10
    return deltas


# extracting features from audio recorded

def extract_features(audio,rate):
    global combined  
    mfcc_feature = mfcc.mfcc(audio, rate, 0.025, 0.01, 20, nfft = 2205, appendEnergy = True)    
    mfcc_feature = preprocessing.scale(mfcc_feature)
#     print(mfcc_feature)
    delta = calculate_delta(mfcc_feature)
    combined = np.hstack((mfcc_feature, delta)) 
    return combined



# function of voice prediction

def predict_person(file_path):
    audio, sr_freq = lr.load(file_path)
    # S = np.abs(lr.stft(audio))

    gmm_files = [ i + '.joblib' for i in ['amira', 'ezzat', 'mariam', 'osama']]
    models    = [joblib.load(fname) for fname in gmm_files]
    x= extract_features(audio, sr_freq)

    
    log_likelihood = np.zeros(len(models)) 
    for j in range(len(models)):
        gmm = models[j] 
        scores = np.array(gmm.score(x))
        log_likelihood[j] = scores.sum()
        

    winner = np.argmax(log_likelihood)
   
    gmm_files2 = [ i + '.joblib' for i in ['closedoor','closelaptop','openbook','opendoor']]
    models2    = [joblib.load(fname) for fname in gmm_files2]
    x2= extract_features(audio, sr_freq)

    
    log_likelihood2 = np.zeros(len(models2)) 
    for j in range(len(models2)):
        gmm2 = models2[j] 
        scores2 = np.array(gmm2.score(x2))
        log_likelihood2[j] = scores2.sum()

    winner2 = np.argmax(log_likelihood2)

    flag2 = False
    flagLst2 = log_likelihood2 - max(log_likelihood2)
    for i in range(len(flagLst2)):
        if flagLst2[i] == 0:
            continue
        if abs(flagLst2[i]) < 0.7:
            flag2 = True
   

    flag = False
    flagLst = log_likelihood - max(log_likelihood)
    for i in range(len(flagLst)):
        if flagLst[i] == 0: 
            continue
        if abs(flagLst[i]) < 0.7:
            flag = True

#   image start 
    plt.figure(figsize=(8, 5))
    x_labl=["amira" , "ezzat" , "mariam" , "osama" ]
    plt.plot(x_labl ,log_likelihood,"ro" , markersize=20)
    y=max(log_likelihood)-1
    if flag:
        y=max(log_likelihood)+2
    plt.axhline(y = y, color = 'b', linestyle = '--' , linewidth=4)
    plt.grid()
    plt.savefig("static/images/signal.png")
#  image  end 

    if flag:
        winner = 4
 
    if winner == 0 and winner2==3 :
        plotFeature(0,log_likelihood[0])
        return "welcome amira Door is now opened"    
    elif winner ==1 and winner2==3:
        plotFeature(1,log_likelihood[1])
        return "welcome ezzat  Door is now opened"
    elif winner ==2 and winner2==3: 
        plotFeature(2,log_likelihood[2])  
        return "welcome mariam  Door is now opened"       
    elif winner ==3 and winner2==3:
        plotFeature(3,log_likelihood[3]) 
        return "welcome osama  Door is now opened" 
    elif winner==0 and winner2 !=3:
        return "Amira Please say open the door  " 
    elif winner==1 and winner2 !=3:
        return "ezzat irPlease say open the door  " 
    elif winner==2 and winner2 !=3:
        return "mariam Please say open the door  " 
    elif winner==3 and winner2 !=3:
        return "osama Please say open the door  " 
    else:
        return "sorry you are not an owner"
 




       


# function of prediction


def predict_scentence(file_path):
    audio, sr_freq = lr.load(file_path)
    S = np.abs(lr.stft(audio))

    gmm_files = [ i + '.joblib' for i in ['closedoor','closelaptop','openbook','opendoor']]
    models    = [joblib.load(fname) for fname in gmm_files]
    x= extract_features(audio, sr_freq)

    
    log_likelihood = np.zeros(len(models)) 
    for j in range(len(models)):
        gmm = models[j] 
        scores = np.array(gmm.score(x))
        log_likelihood[j] = scores.sum()

    # winner = np.argmax(log_likelihood)
    # flag = False
    # flagLst = log_likelihood - max(log_likelihood)
    # for i in range(len(flagLst)):
    #     if flagLst[i] == 0:
    #         continue
    #     if abs(flagLst[i]) < 0.7:
    #         flag = True

    # if flag:
    #     winner = 5
    # if winner ==3:
    #     return "Correct Password"
    # else :
    #     return "Wrong Password"









@app.route('/')
def root():
    return render_template('index.html') 

 
@app.route('/predict', methods=['POST'])
def save_record():
    if request.files['file']:
        file = request.files['file'] 
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(file.filename))
        file_path += '.wav'
        file.save(file_path)
        return jsonify({
                    'person':predict_person(file_path),
                    'sentence':predict_scentence(file_path)
                })
    return 400

if __name__ == '__main__':
    app.run(debug=True, port=11114)
   