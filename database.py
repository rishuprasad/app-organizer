import sqlite3


conn = sqlite3.connect('applications.db')

# conn.execute('''DROP TABLE info''')
# conn.execute('''DROP TABLE status''')

conn.execute('''CREATE TABLE IF NOT EXISTS info
            (app_id VARCHAR(50) PRIMARY KEY NOT NULL,
            company VARCHAR(50) NOT NULL,
            role VARCHAR(50) NOT NULL,
            term VARCHAR(50) NOT NULL)''')

conn.execute('''CREATE TABLE IF NOT EXISTS status
            (app_id VARCHAR(50) PRIMARY KEY NOT NULL,
            date_applied VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            first VARCHAR(50),
            second VARCHAR(50),
            extra VARCHAR(50),
            offer VARCHAR(50) )''')

conn.execute('''CREATE TABLE IF NOT EXISTS assessments
            (app_id VARCHAR(50) PRIMARY KEY NOT NULL,
            deadline VARCHAR(50) NOT NULL''')

conn.execute('''CREATE TABLE IF NOT EXISTS referrals
            (app_id VARCHAR(50) PRIMARY KEY NOT NULL,
            referrer VARCHAR(50) NOT NULL''')


conn.close() 