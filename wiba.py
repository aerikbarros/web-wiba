from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_racer_names():

    # Make a GET request to the main website
    main_page = requests.get('https://zak.stunts.hu')
    soup_main = BeautifulSoup(main_page.content, 'html.parser')
    current_race = soup_main.find(class_='cr-track-details').find('a')['href']
    url = "https://zak.stunts.hu" + current_race
      
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    racer_names = []

    # Extraction of the racers names
    racer_elements = soup.find_all(class_='racer')
    for racer in racer_elements:
        racer_names.append(racer.text.strip())

    return racer_names

@app.route('/')
def index():
    racer_names = scrape_racer_names()  # Call function to get racers names

    return render_template('index.html', racer_names=racer_names)

@app.route('/calculate', methods=['POST'])
def calculate():
    choice = int(request.form['racer_number'])
    
    # Make a GET request to the main website
    main_page = requests.get('https://zak.stunts.hu')
    soup_main = BeautifulSoup(main_page.content, 'html.parser')
    current_race = soup_main.find(class_='cr-track-details').find('a')['href']
    link = "https://zak.stunts.hu" + current_race

    # Make a GET request to the current race track URL
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find scoreboard and car coefficients
    scoreboard_data = soup.find(class_='scoreboard')
    car_elements = soup.select('.sc-label')
    value_elements = soup.select('.sc-value')

    cars = [car.text.strip() for car in car_elements]
    values = [float(value.text.strip().rstrip('%')) / 100 for value in value_elements]

    car_values = list(zip(cars, values))

    # Find all racer data elements using their HTML classes
    racer_data = scoreboard_data.find_all(class_='racer')
    time_data = scoreboard_data.find_all(class_='time')
    car_data = [car.find(class_='car-image')['alt'] for car in scoreboard_data.find_all(class_='car')]

    # Create dictionaries to store racer times and cars
    racer_times = {}
    racer_car = {}

    # Extract racer names, times, and cars
    for racer, time, car in zip(racer_data, time_data, car_data):
        racer_name = racer.text.strip()
        racer_times[racer_name] = time
        racer_car[racer_name] = car

    # Calculate the time based on the chosen racer time
    chosen_racer = list(racer_times.keys())[choice-1]
    chosen_time = racer_times[chosen_racer]
    chosen_car = racer_car[chosen_racer]

    time_string = chosen_time.text.strip().split()[0]
    minutes, seconds = map(float, time_string.split(':'))
    time_float = minutes * 60 + seconds

    # Calculate and print goal times for each car
    racer_value = None
    results = []
    for i, (car, value) in enumerate(car_values):
        if car == chosen_car:
            racer_value = value
        calc_frame = int(calc_total * 20)
        calc_min = calc_frame // 1200
        calc_remainder = calc_frame % 1200
        calc_seg = calc_remainder // 20
        calc_centi = 5 * (calc_remainder % 20)
        results.append(f"{car}: {calc_min}:{calc_seg:02}.{calc_centi:02}")

    if racer_value is None:
        results.append("Car value not found in the table")

    return render_template('results.html', racer=chosen_racer, car=chosen_car, time=time_string, results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
