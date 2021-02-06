import requests
import secrets


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
        another_page = next_page(page, int(json_data["metadata"]["total"])//int(json_data["metadata"]["per_page"]))
        if another_page:
            page += 1
    print("Finished Loading.")
    return all_data


# Checks to see whether there is another page to pull data from
# Returns True if there is and False if there isn't
def next_page(page, total_page):
    if page == total_page:
        return False
    else:
        print("{:.2f}".format(page/total_page * 100), "%")
        return True


# Main function that saves data from the website into a .txt file
def main():
    f = open("School_Data.txt", "w")
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2," \
          "3&fields=id,school.state,school.name,school.city,2018.student.size," \
          "2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line," \
          "2016.repayment.3_yr_repayment.overall"
    all_data = get_data(url)
    print("Writing File.")
    for item in all_data:
        f.write(str(item))
        f.write("\n")
    print("File Completed.")
    f.close()


# If running to get functions dont run main
# If running to run, run main
if __name__ == '__main__':
    main()
