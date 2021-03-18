import requests
import secrets
import sqlite3
import pandas as pd
import sys
import guiwindow
import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import init_notebook_mode, iplot
from typing import Tuple

init_notebook_mode(connected=True)
pio.renderers.default = 'browser'


# Actually gets the data from one page and saves it to an array
def get_data(url: str):
    all_data = []
    page = 0
    another_page = True
    print("Loading data from website: ")
    while another_page:
        full_url = f"{url}&api_key={secrets.api_key}&page={page}"
        response = requests.get(full_url)
        if response.status_code != 200:
            print(response.text)
            return []
        json_data = response.json()
        results = json_data['results']
        all_data.extend(results)
        another_page = next_page(page, int(json_data["metadata"]["total"]) // int(json_data["metadata"]["per_page"]))
        if another_page:
            page += 1
    print("Finished Loading.")
    return all_data


def generate_map(conn):
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }

    employ_df = pd.read_sql_query("SELECT * from employment", conn)
    employ_df.info()
    for item in employ_df.values:
        employ_df['area'] = employ_df['area'].replace(item[0], us_state_abbrev[item[0]])

    school_df = pd.read_sql_query("SELECT * from schools", conn)
    num_jobs = {}
    for item in employ_df.values:
        num_jobs[item[0]] = 0
    for item in employ_df.values:
        num_jobs[item[0]] += item[3]

    print(num_jobs)

    state_data = {}
    for item in school_df.values:
        state_data[item[2]] = 0
    for item in school_df.values:
        state_data[item[2]] += item[4]
    for item in state_data:
        state_data[item] = state_data[item] // 4

    jobs_final_dict = {'states': num_jobs.keys(), 'jobs': num_jobs.values()}
    school_final_dict = {'states': state_data.keys(), 'grads': state_data.values()}
    jobs_final_df = pd.DataFrame(jobs_final_dict, columns=['states', 'jobs'])
    school_final_df = pd.DataFrame(school_final_dict, columns=['states', 'grads'])

    data = dict(type='choropleth', colorscale='Viridis', locations=school_final_df['states'],
                locationmode='USA-states', z=(school_final_df['grads'] // 4), text=school_final_df['states'],
                colorbar={'title': 'Graduates'})
    layout = dict(title='Graduates', geo=dict(projection={'type': 'mercator'}))
    choromap = go.Figure(data=[data], layout=layout)
    choromap.update_geos(visible=False, resolution=50, scope='north america', showcountries=True, countrycolor='Black',
                         showsubunits=True, subunitcolor='Black')

    jobs_data = dict(type='choropleth', colorscale='Viridis', locations=jobs_final_df['states'],
                     locationmode='USA-states', z=(jobs_final_df['jobs']), text=jobs_final_df['states'],
                     colorbar={'title': 'Jobs'})
    jobs_layout = dict(title='Jobs', geo=dict(projection={'type': 'mercator'}))
    jobs_choromap = go.Figure(data=[jobs_data], layout=jobs_layout)
    jobs_choromap.update_geos(visible=False, resolution=50, scope='north america', showcountries=True,
                              countrycolor='Black',
                              showsubunits=True, subunitcolor='Black')
    iplot(jobs_choromap, validate=True)
    iplot(choromap, validate=True)


# Getting data from excel sheet
def get_xlsx(xlsx_file):
    occu_data = pd.read_excel(xlsx_file, sheet_name='State_M2019_dl')
    return occu_data


# Opens DB
def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_conn = sqlite3.connect(filename)  # Connect to a db or create a new one
    cursor = db_conn.cursor()  # Get ready to read or write data
    return db_conn, cursor


# Closes DB
def close_db(conn: sqlite3.Connection):
    conn.commit()  # Save changes
    conn.close()


# Setup another table within the existing database of occupational data
def setup_occdb(cursor: sqlite3.Cursor):
    cursor.execute("""DROP TABLE IF EXISTS employment""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS employment(
    area TEXT NOT NULL,
    occu_code TEXT NOT NULL,
    occupation_major TEXT NOT NULL,
    total_employment INTEGER DEFAULT 0,
    sal_25_perc INTEGER DEFAULT 0);""")


# Setup the database with a table called schools that holds all the data
def setup_db(cursor: sqlite3.Cursor):
    cursor.execute("""DROP TABLE IF EXISTS schools""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS schools(
    school_id INTEGER PRIMARY KEY,
    school_name TEXT NOT NULL,
    school_state TEXT NOT NULL,
    school_city TEXT NOT NULL,
    student_size_2018 INTEGER DEFAULT 0,
    student_size_2017 INTEGER DEFAULT 0,
    earnings_2017 INTEGER DEFAULT 0,
    repayment_2016 INTEGER DEFAULT 0,
    repayment_2016_declining INTEGER DEFAULT 0);""")


# Populates new database with information from occupational data
def populate_employment(cursor: sqlite3.Cursor, employment):
    for item in employment.values:
        if item[9] == 'major':
            if item[7][0] != '3' and item[7][0] != '4':
                cursor.execute("""INSERT INTO EMPLOYMENT (area, occu_code, occupation_major, total_employment, sal_25_perc)
                VALUES (?, ?, ?, ?, ?)""", (item[1], item[7], item[8], item[10], item[24]))


# Populates the DB with the schools pulled from the API website
def populate_db(cursor: sqlite3.Cursor, schools):
    for item in schools:
        cursor.execute("""INSERT INTO SCHOOLS (school_id, school_name, school_state, school_city,
        student_size_2018, student_size_2017, earnings_2017, repayment_2016, repayment_2016_declining)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (item['id'], item['school.name'], item['school.state'], item['school.city'],
                        item['2018.student.size'],
                        item['2017.student.size'],
                        item['2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line'],
                        item['2016.repayment.3_yr_repayment.overall'],
                        item['2016.repayment.repayment_cohort.3_year_declining_balance']))


# Checks to see whether there is another page to pull data from
# Returns True if there is and False if there isn't
def next_page(page, total_page):
    if page == total_page:
        return False
    else:
        print("{:.2f}".format(page / total_page * 100), "%")
        return True


def commit_changes(conn):
    conn.commit()


# Main function that saves data from the website into a .txt file
# Also populates a new table with data from excel sheet
def main():
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2," \
          "3&fields=id,school.state,school.name,school.city,2018.student.size," \
          "2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line," \
          "2016.repayment.3_yr_repayment.overall,2016.repayment.repayment_cohort.3_year_declining_balance"
    conn, cursor = open_db('school_db.sqlite')
    # setup_db(cursor)
    # setup_occdb(cursor)
    app = guiwindow.QApplication(sys.argv)
    ex = guiwindow.Window(url, cursor, conn)
    sys.exit(app.exec_())
    # all_data = get_data(url)
    # employment = get_xlsx(xls_file)
    # populate_db(cursor, all_data)
    # populate_employment(cursor, employment)


# If running to get functions dont run main
# If running to run, run main
if __name__ == '__main__':
    main()
