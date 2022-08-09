
# neccessary imports
import sqlite3
from flask import *
from numpy import full, product
from werkzeug.utils import secure_filename
from datetime import date
import pandas as pd


app = Flask(__name__)
app.secret_key = 'random string'


status_colors = {"Submitted" : "success", "APPLY" : "warning", "" : "secondary"}
colored = False
search_fields = {"company": "", "term": "", "status": ""}


# initial page of the website with no filtering (all records)
@app.route('/', methods=['POST', 'GET'])
def begin():
    # session.clear() clear the current session if there was a previously logged in user
    # print(search_fields)
    global search_fields
    global colored
    if request.method == 'POST':
        colored = True if request.form.getlist('rows_colored') else False
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT i.company as Company, i.app_id as 'Application ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status, s.first as 'First Interview?', s.second as 'Second Interview', s.extra as 'Extra Interviews', s.offer as 'Offer' 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id 
                WHERE i.company LIKE '%{}%' AND i.term LIKE '%{}%' AND s.status LIKE '%{}%' """.format(search_fields["company"], search_fields["term"], search_fields["status"]), 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('index.html', app_data=app_data, search_fields=search_fields, colored=colored, field_colors=status_colors, field="Status")


# handles any search criteria
@app.route('/search', methods = ['POST'])
def search():
    if request.method == 'POST':    # gather info from HTML text boxes
        global search_fields
        search_fields["company"] = request.form["company"]
        search_fields["term"] = request.form['term']
        search_fields["status"] = request.form['status']
        return redirect(url_for('begin'))


# route to search page
@app.route('/to_search', methods = ['GET'])
def to_search():
    if request.method == "GET":
        return redirect(url_for('begin'))


# route to insert page
@app.route('/to_insert', methods = ['GET'])
def to_insert():
    if request.method == "GET":
        return redirect(url_for('insert_page'))


# page for inserting new apps
@app.route('/insert', methods=['POST', 'GET'])
def insert_page():
    global search_fields
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT i.company as Company, i.app_id as 'Application ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status, s.first as 'First Interview?', s.second as 'Second Interview', s.extra as 'Extra Interviews', s.offer as 'Offer' 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id """, 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('insert.html', app_data=app_data)




# already logged in
# @app.route('/home') # This function is for the home page of the website once the user has logged in
# def home():
#     isAdmin = False
#     if 'admin' in session:  # change page layout depending on admin privs
#         isAdmin = True

#     loggedIn, first_name = getLoginDetails() # Helper function to dispay the user's name on the home page
 
#     with sqlite3.connect('store.db') as conn: # Connects to database and displays the products
#         cur = conn.cursor()
#         cur.execute('SELECT product_id, product_name, inventory, price, image FROM product')
#         itemData = cur.fetchall()
#     itemData = parse(itemData) 

#     return render_template('index.html', itemData=itemData, loggedIn=loggedIn, first_name=first_name.title(), isAdmin=isAdmin) # sets the current frame to index.html w/ the user's name displayed at the top


if __name__ == '__main__':
   
   app.run(port='8000', debug=True)
