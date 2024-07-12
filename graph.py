
import matplotlib.pyplot as plt
from models import *


def bar_graph():
        r1 = Song.query.filter(Song.rating.between(0.0,1.0)).all()
        r2 = Song.query.filter(Song.rating.between(1.0,2.0)).all()
        r3 = Song.query.filter(Song.rating.between(2.0,3.0)).all()
        r4 = Song.query.filter(Song.rating.between(3.0,4.0)).all()
        r5 = Song.query.filter(Song.rating.between(4.0,5.0)).all()
       
        d = {'0.0-1.0': 0, '1.0-2.0': 0, '2.0-3.0': 0, '3.0-4.0': 0}
        d['0.0-1.0']=len(r1)
        d['1.0-2.0']=len(r2)
        d['2.0-3.0']=len(r3)
        d['3.0-4.0']=len(r4)
        d['4.0-5.0']=len(r5)
        labels=d.keys()
        values=d.values()
        plt.bar(labels, values, color='blue')
        plt.xlabel('Ratings')
        plt.ylabel('No. of songs')
        plt.title('Bar Graph')
        plt.savefig('C:\project music app\static\BarGraph.jpeg')
        plt.clf()

def pie_chart():
        u = User.query.filter_by(role="user").all()
        user_count = len(u)
        c= User.query.filter_by(role="creator").all()
        creator_count = len(c)
        data ={"TOTAL USERS":0, "CREATORS":0 , "USERS NOT CREATORS":0}
        data["TOTAL USERS"]=user_count+creator_count
        data["CREATORS"]=creator_count
        data["USERS NOT CREATORS"]=user_count
        labels=data.keys()
        sizes=data.values()
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title("piechart")
        plt.savefig('C:\project music app\static\PieChart.jpeg')
        plt.clf()