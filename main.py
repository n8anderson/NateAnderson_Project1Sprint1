import requests
import secrets
import sqlite3
import pandas as pd
import sys
import guiwindow
import plotly.graph_objs as go
from plotly.offline import iplot
from typing import Tuple


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


# Gets the abbreviations for each state (as heat maps only like abbreviations)
def get_abbrev(key):
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

    return us_state_abbrev[key]


# Gets the employment data from sql
def get_from_employment(conn):
    return pd.read_sql_query("SELECT * from employment", conn)


# Returns the desired ratio
def get_ratio(x_ratio, y_ratio):
    ratio = {}
    for item in x_ratio.keys():
        if y_ratio.__contains__(item):
            ratio[item] = y_ratio[item] / x_ratio[item]
    ratio_df = {'states': ratio.keys(), 'ratio': ratio.values()}
    return ratio_df


# Returns the average salaries for all of the states and territories
def get_average_salaries(conn):
    salary_df = get_from_employment(conn)
    for item in salary_df.values:
        salary_df['area'] = salary_df['area'].replace(item[0], get_abbrev(item[0]))

    counts = {}
    average_salaries = {}
    for item in salary_df.values:
        average_salaries[item[0]] = 0
        counts[item[0]] = 0
    for item in salary_df.values:
        if type(item[4]) is int:
            average_salaries[item[0]] += item[4]
            counts[item[0]] += 1
    for item in average_salaries:
        average_salaries[item] /= counts[item]

    return average_salaries


# Returns the average repayment values for all of the states and territories
def get_repayment_values(conn):
    repayment_df = pd.read_sql_query("SELECT * from schools", conn)
    repayment_values = {}
    counts = {}
    for item in repayment_df.values:
        repayment_values[item[2]] = 0
        counts[item[2]] = 0
    for item in repayment_df.values:
        if str(item[8]) != 'nan':
            repayment_values[item[2]] += float(item[8])
            counts[item[2]] += 1

    for item in repayment_values:
        if counts[item] != 0:
            repayment_values[item] /= counts[item]

    return repayment_values


# Generates a heat map for the average salaries throughout the US
def generate_wage_map(conn):
    average_salaries = get_average_salaries(conn)

    repayment_values = get_repayment_values(conn)

    wage_ratio = get_ratio(repayment_values, average_salaries)
    wage_ratio_df = pd.DataFrame(wage_ratio, columns=['states', 'ratio'])

    ratio_data = dict(type='choropleth', colorscale='Viridis', locations=wage_ratio_df['states'],
                      locationmode='USA-states', z=(wage_ratio_df['ratio']), text=wage_ratio_df['states'],
                      colorbar={'title': 'Salaries Considering Declining Balance'})
    ratio_layout = dict(title='Salaries Vs Declining Balance', geo=dict(projection={'type': 'mercator'}))
    ratio_map = go.Figure(data=[ratio_data], layout=ratio_layout)
    ratio_map.update_geos(visible=False, resolution=50, scope='north america', showcountries=True,
                          countrycolor='Black',
                          showsubunits=True, subunitcolor='Blue')

    iplot(ratio_map, validate=True)


# Gets the data from employment library and returns the dictionary
def get_employment(conn):
    employ_df = get_from_employment(conn)
    for item in employ_df.values:
        employ_df['area'] = employ_df['area'].replace(item[0], get_abbrev(item[0]))
    num_jobs = {}
    for item in employ_df.values:
        num_jobs[item[0]] = 0
    for item in employ_df.values:
        num_jobs[item[0]] += item[3]
    return num_jobs


# Gets the data from the school library and returns the dictionary
def get_school_data(conn):
    school_df = pd.read_sql_query("SELECT * from schools", conn)
    state_data = {}
    for item in school_df.values:
        state_data[item[2]] = 0
    for item in school_df.values:
        state_data[item[2]] += item[4]
    for item in state_data:
        state_data[item] = state_data[item] // 4
    return state_data


# Generating the heat map based off of the data that is pulled
def generate_map(conn):
    num_jobs = get_employment(conn)

    state_data = get_school_data(conn)

    employment_dict = get_ratio(state_data, num_jobs)
    employment_df = pd.DataFrame(employment_dict, columns=['states', 'ratio'])
    data = dict(type='choropleth', colorscale='Viridis', locations=employment_df['states'],
                locationmode='USA-states', z=(employment_df['ratio']), text=employment_df['states'],
                colorbar={'title': 'Jobs per Graduate'})
    layout = dict(title='Jobs Per Graduate', geo=dict(projection={'type': 'mercator'}))
    choromap = go.Figure(data=[data], layout=layout)
    choromap.update_geos(visible=False, resolution=50, scope='north america', showcountries=True, countrycolor='Black',
                         showsubunits=True, subunitcolor='Black')
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
                cursor.execute("""INSERT INTO EMPLOYMENT (area, occu_code, occupation_major, total_employment,
                sal_25_perc) VALUES (?, ?, ?, ?, ?)""", (item[1], item[7], item[8], item[10], item[24]))


# Populates the DB with the schools pulled from the API website
def populate_db(cursor: sqlite3.Cursor, schools):
    for item in schools:
        cursor.execute("""INSERT INTO SCHOOLS (school_id, school_name, school_state, school_city,
        student_size_2018, student_size_2017, earnings_2017, repayment_2016, repayment_2016_declining)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (item['id'], item['school.name'], item['school.state'],
                        item['school.city'],
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
    setup_db(cursor)
    setup_occdb(cursor)
    app = guiwindow.QApplication(sys.argv)
    ex = guiwindow.Window(url, cursor, conn)
    ex.isHidden()
    sys.exit(app.exec_())


# If running to get functions dont run main
# If running to run, run main
if __name__ == '__main__':
    main()
