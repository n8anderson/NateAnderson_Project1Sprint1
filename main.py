import requests
import secrets

def get_data(url:str):
    all_data = []
    full_url = f"{url}&api_key={secrets.api_key}&page=3"
    response = requests.get(full_url)
    if response.status_code != 200:
        print(response.text)
        return []
    json_data = response.json()
    results = json_data['results']
    all_data.extend(results)
    return all_data

def main():
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id,school.state,school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line,2016.repayment.3_yr_repayment.overall"
    all_data = get_data(url)
    for item in all_data:
        print(item)

#If running to get functions dont run main
#If running to run, run main
if __name__ == '__main__':
    main()