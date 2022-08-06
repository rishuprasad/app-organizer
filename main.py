
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


# Rishabh Prasad
# initial index page of the website (no user should be logged in)
@app.route('/')
def begin():
    session.clear() # clear the current session if there was a previously logged in user
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT i.company as Company, i.app_id as 'Application ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status, s.first as 'First Interview?', s.second as 'Second Interview', s.extra as 'Extra Interviews', s.offer as 'Offer' 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id """, 
                conn)
    print(app_info)
    app_data = app_info.to_dict('record')
    print(app_data)
    return render_template('index.html', app_data=app_data, colored=True, field_colors=status_colors, field="Status")

# Christopher Lynch
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
