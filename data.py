from flask import Flask
app = Flask(__name__)  #__name__ 代表目前執行的模組

@app.route("/") # 函式的裝飾 已函示為基礎 提供附加的功能
def home():
    return "Hello"

@app.route("/test")  #代表要處理的網站路徑
def test():
    return "WORLD"


#if __name__ == "__main__": #如果以主程式執行
#    app.run()

# import os.path
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, "test1.db")

import sqlite3
db_file = "test1.db"


def create(db_file):
    conn = sqlite3.connect(db_file)

    c = conn.cursor()
    c.execute(c.execute('''CREATE TABLE DataBase   
        (DATE           TEXT    NOT NULL,
        EVENT           TEXT    NOT NULL);'''))
    conn.commit()
    conn.close()

def insert(db_file,date,event):
    conn = sqlite3.connect(db_file)

    c = conn.cursor()
    
    c.execute("INSERT INTO DataBase (DATE,EVENT) \
      VALUES ('"+date+"', '"+event+"' )")


    conn.commit()
    conn.close()

def select_all(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    cursor = c.execute("SELECT DATE, EVENT  from DataBase")
    for row in cursor:
        print ("Date = ", row[0])
        print ("Event = ", row[1])

    conn.close()
def delete(db_file,date):    
    conn = sqlite3.connect(db_file)
    c = conn.cursor()


    c.execute("DELETE from DataBase where DATE='"+date+"';")
    conn.commit()

    conn.close()

#create(db_file)
#insert(db_file,"2021年10月11日","成大操場")
delete(db_file,"10月")

select_all(db_file)