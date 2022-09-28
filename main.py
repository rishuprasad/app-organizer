
# neccessary imports
import sqlite3
from flask import *
from numpy import full, product
from werkzeug.utils import secure_filename
from datetime import date
import pandas as pd


app = Flask(__name__)
app.secret_key = 'random string'


status_colors = {"NTA" : "danger", "Submitted" : "primary", "Interviewing" : "warning", "Rejected" : "info", "Offer" : "success"}
colored = False
search_fields = {"company": "", "term": "", "status": ""}
term_options = {"fall_2022": "Fall 2022", "winter_2023": "Winter 2023", "spring_2023": "Spring 2023", "summer_2023": "Summer 2023", "fall_2023": "Fall 2023", "general": "General"}
status_options = {"status_apply": "NTA", "status_submit": "Submitted", "status_assess": "Assessment", "status_interview": "Interviewing", "status_reject": "Rejected", "status_offer": "Offer"}
tbl_info = {"Application ID": 'app_id', "Company": 'company', "Role": 'role', "Term": 'term'}
tbl_status = {"Application ID": "app_id", "Date Applied": "date_applied", "Status": "status", "First Interview": "`first`", "Second Interview": "second", "Extra Interviews": "extra", "Offer": "offer"}
blank_val = "-"
info_columns = "i.company as Company, i.app_id as 'ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status"
specific_app_cols = "i.company as Company, i.app_id as 'ID', i.role as Role, i.term as Term, s.date_applied as 'Date Applied', s.status as Status, s.assessment as 'Assessment', s.first as 'First Interview', s.second as 'Second Interview', s.extra as 'Extra Interviews', s.offer as Offer"
edit_fields = {"Assessment": ('Assigned', 'Completed'), "First Interview": ("Scheduled", "Completed"), "Second Interview": ("Scheduled", "Completed"), "Extra Interviews": ("Scheduled", "Completed"), "Offer": ("Accepted", "Rejected")}

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
            """ SELECT {} 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id 
                WHERE i.company LIKE '%{}%' AND i.term LIKE '%{}%' AND s.status LIKE '%{}%' """.format(info_columns, search_fields["company"], search_fields["term"], search_fields["status"]), 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('index.html', app_data=app_data, len=len(app_data), search_fields=search_fields, colored=colored, field_colors=status_colors, field="Status")


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
            """ SELECT {} 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id """.format(info_columns), 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('insert.html', app_data=app_data, term_options=term_options, status_options=status_options)


# inserts new records
@app.route('/insert_new', methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':    # gather info from HTML text boxes
        app_id = blank_val if not request.form.getlist("app_id") else request.form["app_id"]
        company = blank_val if not request.form.getlist("company") else request.form["company"]
        role = blank_val if not request.form.getlist("role") else request.form["role"]
        term = blank_val if not request.form.getlist("term") else term_options[request.form["term"]]
        date_applied = blank_val if not request.form.getlist("date_applied") else request.form["date_applied"] 
        status = blank_val if not request.form.getlist("status") else status_options[request.form["status"]]
        with sqlite3.connect('applications.db') as conn: # query for all application info
            cur = conn.cursor()
            cur.execute('INSERT INTO info (app_id, company, role, term) VALUES (?, ?, ?, ?)', (app_id, company, role, term))                
            conn.commit()
            cur.execute('INSERT INTO status (app_id, date_applied, status) VALUES (?, ?, ?)', (app_id, date_applied, status))                
            conn.commit()
        return redirect(url_for('insert_page'))


# page for deleting app records
@app.route('/delete', methods=['POST', 'GET'])
def delete_page():
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT {} 
                FROM info as i LEFT JOIN status as s ON i.app_id = s.app_id """.format(info_columns), 
                conn)
    app_data = app_info.to_dict('records')
    return render_template('delete.html', app_data=app_data)


# delete an entry
@app.route('/delete_entry', methods=['GET'])
def delete():
    if request.method == "GET":
        record = request.args.get('record')
        record = record.replace('\'', '')
        record = record.replace(': ', ':')
        record = record[1:-1].split(',')
        record = [(i.split(':')[0].strip(), i.split(':')[1].strip()) for i in record]
        query1 = "DELETE FROM info WHERE "
        query2 = "DELETE FROM status WHERE "
        for field in record:
            if field[1] == "None":
                continue
            if field[0] in tbl_info:
                query1 += "\"" + tbl_info[field[0]] + "\"" + "=" + "\"" + field[1] + "\" AND "
            if field[0] in tbl_status:
                query2 += "\"" + tbl_status[field[0]] + "\"" + "=" + "\"" + field[1] + "\" AND "
        query1 += "0=0"
        query2 += "0=0"
        with sqlite3.connect('applications.db') as conn: # delete all associated info for the app_id
                cur = conn.cursor()
                cur.execute(query1)                
                conn.commit()
                cur.execute(query2)                
                conn.commit()
    return redirect(url_for('delete_page'))


# route to delete page
@app.route('/to_delete', methods = ['GET'])
def to_delete():
    if request.method == "GET":
        return redirect(url_for('delete_page'))


# page for individual app info
@app.route('/app_page', methods=['POST', 'GET'])
def app_page():
    app_id = request.args.get('app_id') # get the app ID from HTML and request
    print(app_id)
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_info = pd.read_sql(
            """ SELECT {} 
                FROM status as s JOIN info as i ON i.app_id = s.app_id 
                WHERE i.app_id = '{}' AND s.app_id = '{}' """.format(specific_app_cols, app_id, app_id), 
                conn)
    app_list = app_info.to_dict('records')[0]
    return render_template('app_page.html', app_list=app_list, edit=False)


# page for editing an app
@app.route('/to_edit', methods=['POST'])
def edit_page():
    if request.method == 'POST':
        app_id = request.args.get('app_id') # get the app ID from HTML and request
        with sqlite3.connect('applications.db') as conn: # query for all application info
            app_info = pd.read_sql(
                """ SELECT {} 
                    FROM status as s JOIN info as i ON i.app_id = s.app_id 
                    WHERE i.app_id = '{}' AND s.app_id = '{}' """.format(specific_app_cols, app_id, app_id), 
                    conn)
        app_list = app_info.to_dict('records')[0]
    return render_template('app_page.html', app_list=app_list, edit=True, edit_fields=edit_fields)


# edit an app's info directly
@app.route('/edit', methods=['POST'])
def edit():
    if request.method == 'POST':
        app_id = request.args.get('app_id') # get the app ID from HTML and request
        assessment = request.form["Assessment"]
        first = request.form["First Interview"]
        second = request.form["Second Interview"]
        extra = request.form["Extra Interviews"]
        offer = request.form["Offer"] 
        with sqlite3.connect('applications.db') as conn: # update status table with relevant selections
            cur = conn.cursor()
            cur.execute(""" UPDATE status as s 
                    SET assessment='{}', first='{}', second='{}', extra='{}', offer='{}'
                    WHERE s.app_id = '{}' """.format(assessment, first, second, extra, offer, app_id))                
            conn.commit()
        update_status(app_id)
    return redirect(url_for('app_page', app_id=app_id))


# updates status based on interviewing status
def update_status(app_id):
    with sqlite3.connect('applications.db') as conn: # query for all application info
        app_status = pd.read_sql(
            """ SELECT s.first, s.second, s.extra, s.offer 
                FROM status as s
                WHERE s.app_id = '{}' """.format(app_id, ), 
                conn)
        app_assess = pd.read_sql(
            """ SELECT s.assessment
                FROM status as s
                WHERE s.app_id = '{}' """.format(app_id, ), 
                conn)
        app_date = pd.read_sql(
             """ SELECT s.date_applied 
                FROM status as s
                WHERE s.app_id = '{}' """.format(app_id, ), 
                conn)
    app_list = app_status.to_dict('records')[0]
    app_assess = app_assess.to_dict('records')[0]
    app_date = app_date.to_dict('records')[0]
    status_update = ""
    if app_list['offer'] == "Extended" or app_list['offer'] == "Accepted":
        status_update = "Offer"
    elif app_list['offer'] == "Rejected":
        status_update = "Rejected"
    elif all([value != 'None' for value in app_list.values()]):
        status_update = "Interviewing"
    elif app_assess['assessment'] != 'None':
        status_update = "Assessment"
    elif app_date['date_applied'] != "":
        status_update = "Submitted"
    else:
        status_update = "NTA"
    with sqlite3.connect('applications.db') as conn: # update status table with relevant selections
            cur = conn.cursor()
            cur.execute(""" UPDATE status as s 
                    SET status='{}'
                    WHERE s.app_id = '{}' """.format(status_update, app_id, ))                
            conn.commit()
    


# deletes application from all tables
@app.route('/delete_from_info', methods=['POST'])
def delete_from_info():
    if request.method == 'POST':
        app_id = request.args.get('app_id')
        with sqlite3.connect('applications.db') as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM status WHERE app_id = ?", (app_id, )) # delete status contents based on app ID
            cur.execute("DELETE FROM info WHERE app_id = ?", (app_id, )) # delete info contents based on app ID
        conn.close()
    return redirect(url_for('begin'))





if __name__ == '__main__':
   
   app.run(port='8000', debug=True)
