# Flask abstracts (simplifies) web development
# render_template allows you to render html templates with specific inputs
# requests lets you extract POSTed user input via request.form['<input namer>']
# url_for allows you to change between webpages
# session allows you to use cookies (trace multiple web requests to a single user)
from flask import Flask, render_template, request, url_for, escape, session
# this imports our own python module
from vsearch4web import Search4Letters
# this makes it easier to open and read/write to databases
# ConnectionError is a user created error that tells you when there is a problem connecting to mySQL
# SQLError is a user created error that tells you when there is a problem in the SQL query
from DBcm import UseDatabase, ConnectionError, SQLError

app = Flask(__name__)

app.secret_key = 'TapTapTapImIn'

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'pw',
                          'database': 'vsearchlogDB',}

app.config['dbconfig2'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'pw',
                          'database': 'icdcodes',}


def log_request(req: 'flask_request') -> None:
    """Log data onto MySQL database"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """ insert into log
                (code, description, confidence)
                values
                (%s, %s, %s)"""
        cursor.execute(_SQL, (req.form['code'],
                            req.form['des'],
                            req.form['confidence']))

# this page just provides a rendering of the data stored in the database
@app.route('/viewlog')
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML"""
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select code, description, confidence
                    from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles = ('code', 'description', 'confidence')
            return render_template('viewlog.html',
                                the_title = 'View Log',
                                the_row_titles = titles,
                                the_data = contents,)
    except ConnectionError as err:
        print(f'Is your database connected? Error: {err}')
    except SQLError as err:
        print(f'Is your query correct? Error: {err}')
    except Exception as err:
        print(f'Something went wrong with error {err}')
    return 'Error'


# this page just provides a rendering of the data stored in the database
@app.route('/viewcodes')
def view_the_db() -> 'html':
    """Display the contents of the icd code database as a HTML"""
    try:
        with UseDatabase(app.config['dbconfig2']) as cursor:
            _SQL = """select CODE, DESCRIPTION
                    from codes"""   
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles = ('CODE', 'DES')
            return render_template('icdallcodes.html',
                                the_title = 'View database',
                                the_row_titles = titles,
                                the_data = contents,)
    except ConnectionError as err:
        print(f'Is your database connected? Error: {err}')
    except SQLError as err:
        print(f'Is your query correct? Error: {err}')
    except Exception as err:
        print(f'Something went wrong with error {err}')
    return 'Error'



# POST must be included if you wish to recieve user input on the page
# app.route() is a function decorator, in this case it converts a function into a webpage 
@app.route("/search4", methods = ['POST'])
def do_search() -> str:
    user_input_code = request.form['code']
    user_input_code = user_input_code.strip()
    #user_input_code = user_input_code.replace(" ", "%")
    if len(user_input_code) == 0:
        user_input_code = '999999999'

    user_input_des = request.form['des']
    user_input_des = user_input_des.strip()
    if len(user_input_des) == 0:
        user_input_des = '99999999999'

    user_input_des = [i for i in user_input_des.split(' ')]
   
    des_search = "(DESCRIPTION like '%" + user_input_des[0] + "%')"
    if len(user_input_des)>1:
        for i in range(1, len(user_input_des)):
            des_search = des_search + "AND (DESCRIPTION like '%" + user_input_des[i] + "%')"

    user_input_slider = request.form['confidence']

    # it is important to protect your database code with try. If the database is unavailable this will prevent the webapp from crashing.
    try:
        log_request(req = request)
    except Exception as err:
        print(f'*****Logging failed with this error: {err}')

    try:
        with UseDatabase(app.config['dbconfig2']) as cursor:
            _SQL = f"""select CODE, DESCRIPTION
                    from codes
                    where CODE like '%{user_input_code}%' OR {des_search}""" 
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles = ('CODE', 'DES')
            return render_template('icdallcodes.html',
                                the_title = 'View database',
                                the_row_titles = titles,
                                the_data = contents,)
    except ConnectionError as err:
        print(f'Is your database connected? Error: {err}')
    except SQLError as err:
        print(f'Is your query correct? Error: {err}')
    except Exception as err:
        print(f'Something went wrong with error {err}')
    return 'Error'
        

@app.route("/")
def entry_page() -> 'html':
    return render_template('entry.html', the_title = 'Welcome to Search4Codes Webapp')

if __name__ == "__main__":
    app.run(debug = True)