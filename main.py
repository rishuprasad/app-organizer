
# neccessary imports
import sqlite3
from flask import *
from numpy import full, product
from werkzeug.utils import secure_filename
from datetime import date
import pandas as pd


app = Flask(__name__)
app.secret_key = 'random string'


status_colors = {"APPLY" : "warning", "Submitted" : "success", "In Progress" : "secondary"}
colored = False
search_fields = {"company": "", "term": "", "status": ""}
term_options = {"fall_2022": "Fall 2022", "winter_2023": "Winter 2023", "spring_2023": "Spring 2023", "summer_2023": "Summer 2023", "fall_2023": "Fall 2023", }
status_options = {"status_apply": "APPLY", "status_submit": "Submitted", "status_in_progress": "In Progress", "status_reject": "Rejected"}


# initial page of the website with no filtering (all records)
@app.route('/', methods=['POST', 'GET'])
def begin():
    # session.clear() clear the current session if there was a previously logged in user
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
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT i.company as Company, i.app_id as 'Application ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status, s.first as 'First Interview?', s.second as 'Second Interview', s.extra as 'Extra Interviews', s.offer as 'Offer' 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id """, 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('insert.html', app_data=app_data)


# inserts new records
@app.route('/insert_new', methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':    # gather info from HTML text boxes
        app_id = request.form["app_id"]
        company = request.form["company"].title()
        role = request.form["role"]
        term = term_options[request.form["term"]]
        date_applied = request.form["date_applied"]
        status = status_options[request.form["status"]]
        with sqlite3.connect('applications.db') as conn: # query for all application info
            cur = conn.cursor()
            cur.execute('INSERT INTO info (app_id, company, role, term) VALUES (?, ?, ?, ?)', (app_id, company, role, term))                
            conn.commit()
            cur.execute('INSERT INTO status (app_id, date_applied, status) VALUES (?, ?, ?)', (app_id, date_applied, status))                
            conn.commit()
        return redirect(url_for('insert_page'))


# page for inserting new apps
@app.route('/delete', methods=['POST', 'GET'])
def delete_page():
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT i.company as Company, i.app_id as 'Application ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status, s.first as 'First Interview?', s.second as 'Second Interview', s.extra as 'Extra Interviews', s.offer as 'Offer' 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id """, 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('delete.html', app_data=app_data)


# route to delete page
@app.route('/to_delete', methods = ['GET'])
def to_delete():
    if request.method == "GET":
        return redirect(url_for('delete_page'))


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
