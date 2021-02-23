import main


# Test to get the information from the API website
def test_getschooldata():
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2," \
          "3&fields=id,school.state,school.name,school.city,2018.student.size," \
          "2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line," \
          "2016.repayment.3_yr_repayment.overall"
    resulting_array = main.get_data(url)
    num_schools = len(resulting_array)
    assert num_schools > 1000


# Test to see if can get the information from excel data
# Passes if it gets all 50 occupational titles from Alabama
def test_getexcel():
    excel_file = 'data_testfile.xlsx'
    test_data = main.get_xlsx(excel_file)
    data = []
    for item in test_data.values:
        data.append(item[8])
    assert len(data) == 50


# Test to see if it creates the data in the database.
# Pushes the excel data to database and pulls it using fetch all
# creates an array of occupational titles, if length is 50,
# then it passes
def test_occudb():
    excel_file = 'data_testfile.xlsx'
    test_data = main.get_xlsx(excel_file)
    conn, cursor = main.open_db('test_db.sqlite')
    main.setup_occdb(cursor)
    main.populate_employment(cursor, test_data)
    cursor.execute("""SELECT * FROM employment""")
    data = cursor.fetchall()
    main.close_db(conn)
    occu_titles = []
    for item in data:
        if not occu_titles.__contains__(item[2]):
            occu_titles.append(item[2])
    assert len(occu_titles) == 2


# Test to insert a school into a new database, and make sure it can be pulled
def test_db():
    schools = [{'id': '1234', 'school.state': 'MA', 'school.name': 'Bridgewater State University',
                'school.city': 'Bridgewater',
                '2018.student.size': 10000,
                '2017.student.size': 9000,
                '2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line': 500,
                '2016.repayment.3_yr_repayment.overall': 100}]
    conn, cursor = main.open_db('test_db.sqlite')
    main.setup_db(cursor)
    main.populate_db(cursor, schools)
    cursor.execute("""SELECT * FROM schools""")
    data = cursor.fetchone()
    main.close_db(conn)
    assert data[1] == 'Bridgewater State University'
