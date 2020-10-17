from datetime import timedelta
from flask import Flask, render_template, g, request, Markup, jsonify, flash
import requests
import json
import os
import flask_monitoringdashboard as dashboard
import requests_cache
from apscheduler.schedulers.background import BackgroundScheduler
import re

expire_after = timedelta(minutes=30)
requests_cache.install_cache('main_cache', expire_after=expire_after)

app = Flask(__name__)
dashboard.bind(app)


@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('pages-404.html'), 404


@app.errorhandler(500)
def internal_server(e):
    # note that we set the 404 status explicitly
    return render_template('pages-500.html'), 500

def remove(string):
    return "".join(string.split())

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)',text)]


def back_job():
    uri = requests.get("https://api.covid19api.com/summary")
    uri1 = requests.get("https://api.covid19india.org/data.json")
    uri2 = requests.get("https://api.covid19india.org/v2/state_district_wise.json")
    uri3 = requests.get("https://api.covid19india.org/resources/resources.json")
    uri4 = requests.get("https://covid.ourworldindata.org/data/owid-covid-data.json")
    uri5 = requests.get("https://api.covid19india.org/raw_data.json")
    uri6 = requests.get("https://api.rootnet.in/covid19-in/hospitals/beds")
    uri7 = requests.get("https://api.rootnet.in/covid19-in/hospitals/medical-colleges")
    uri8 = requests.get("https://api.rootnet.in/covid19-in/contacts")
    uri9 = requests.get("https://api.covid19india.org/v4/data.json")


sched = BackgroundScheduler(daemon=True)
sched.add_job(back_job, 'interval', minutes=10)
sched.start()


@app.route('/index/globalData', methods=["GET"])
def globalData():
    worldDataResponse = requests.get("https://api.covid19api.com/summary")
    jsonResponse = json.loads(worldDataResponse.content)
    worldTotal = jsonResponse['Global']['TotalConfirmed']
    worldDeceased = jsonResponse['Global']['TotalDeaths']
    worldRecovered = jsonResponse['Global']['TotalRecovered']

    worldNewCases = jsonResponse['Global']['NewConfirmed']
    worldNewDeceases = jsonResponse['Global']['NewDeaths']
    worldNewRecovered = jsonResponse['Global']['NewRecovered']

    world = [worldTotal, worldDeceased, worldRecovered, worldNewCases, worldNewDeceases, worldNewRecovered]
    return jsonify(world)


@app.route('/index/india', methods=["GET"])
def indiaData():
    stateDataResponse = requests.get("https://api.covid19india.org/v4/data.json")
    jsonData = json.loads(stateDataResponse.content)

    indTested = jsonData['TT']['total']['tested']
    indConfirmed = jsonData['TT']['total']['confirmed']
    indDeceased = jsonData['TT']['total']['deceased']
    indRecovered = jsonData['TT']['total']['recovered']

    indDeltaConfirmed = jsonData['TT']['delta']['confirmed']
    indDeltaRecovered = jsonData['TT']['delta']['recovered']
    indDeltaDeaths = jsonData['TT']['delta']['deceased']
    indlastupdatedtime = jsonData['TT']['meta']['last_updated']
    indpopulation = jsonData['TT']['meta']['population']

    india = [indTested, indConfirmed, indDeceased, indRecovered, indDeltaConfirmed, indDeltaRecovered, indDeltaDeaths,
             indlastupdatedtime, indpopulation]

    return jsonify(india)


@app.route('/')
def home():
    ip = request.remote_addr
    with open("userdata.txt", "r+") as f:
        line_found = any(ip in line for line in f)
        if not line_found:
            f.seek(0, os.SEEK_END)
            f.write(request.remote_addr + "\n")

    return render_template('index.html')


@app.route('/states')
def stateNames():
    stateDataResponse = requests.get("https://api.covid19india.org/data.json")
    jsonData = json.loads(stateDataResponse.content)
    stateData = []
    stateLen = len(jsonData['statewise'])
    for states in range(0, stateLen):
        stateData.append(str(jsonData['statewise'][states]['state']))
    return render_template('states.html', stateData=stateData)


@app.route('/states/<stateName>')
def stateData(stateName):
    stateDataResponse = requests.get("https://api.covid19india.org/data.json")
    jsonData = json.loads(stateDataResponse.content)
    stateData = []
    stateLen = len(jsonData['statewise'])
    for states in range(0, stateLen):
        stateData.append(str(jsonData['statewise'][states]['state']))

    districtDataResponse = requests.get("https://api.covid19india.org/v2/state_district_wise.json")
    distjsonData = json.loads(districtDataResponse.content)

    stateContent = {}
    stateLen = len(jsonData['statewise'])
    for states in range(0, stateLen):
        name = str(jsonData['statewise'][states]['state'])
        if name == stateName:
            stateContent[str(jsonData['statewise'][states]['state'])] = {}
            stateContent[str(jsonData['statewise'][states]['state'])] = {}
            stateContent[str(jsonData['statewise'][states]['state'])]["active"] = jsonData['statewise'][states][
                'active']
            stateContent[str(jsonData['statewise'][states]['state'])]["confirmed"] = jsonData['statewise'][states][
                'confirmed']
            stateContent[str(jsonData['statewise'][states]['state'])]["deaths"] = jsonData['statewise'][states][
                'deaths']
            stateContent[str(jsonData['statewise'][states]['state'])]["recovered"] = jsonData['statewise'][states][
                'recovered']
            stateContent[str(jsonData['statewise'][states]['state'])]["lastupdatedtime"] = \
            jsonData['statewise'][states][
                'lastupdatedtime']
            stateContent[str(jsonData['statewise'][states]['state'])]["deltaconfirmed"] = \
                jsonData['statewise'][states][
                    'deltaconfirmed']
            stateContent[str(jsonData['statewise'][states]['state'])]["deltadeaths"] = \
                jsonData['statewise'][states][
                    'deltadeaths']
            stateContent[str(jsonData['statewise'][states]['state'])]["deltarecovered"] = \
                jsonData['statewise'][states][
                    'deltarecovered']
            stateContent[str(jsonData['statewise'][states]['state'])]["statenotes"] = jsonData['statewise'][states][
                'statenotes']
    districtData = {}
    for states in range(0, 37):
        districtLen = len(distjsonData[states]['districtData'])
        for district in range(0, districtLen):
            name = str(distjsonData[states]['state'])
            if name == stateName:
                dist = str(distjsonData[states]['districtData'][district]['district'])
                districtData[str(distjsonData[states]['districtData'][district]['district'])] = {}
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["active"] = \
                    distjsonData[states]['districtData'][district]['active']
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["confirmed"] = \
                    distjsonData[states]['districtData'][district]['confirmed']
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["deceased"] = \
                    distjsonData[states]['districtData'][district]['deceased']
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["recovered"] = \
                    distjsonData[states]['districtData'][district]['recovered']
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["deltaconfirmed"] = \
                    distjsonData[states]['districtData'][district]['delta']['confirmed']
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["deltadeceased"] = \
                    distjsonData[states]['districtData'][district]['delta']['deceased']
                districtData[str(distjsonData[states]['districtData'][district]['district'])]["deltarecovered"] = \
                    distjsonData[states]['districtData'][district]['delta']['recovered']

    stateContent[stateName]['district'] = districtData

    return render_template('statesData.html', stateContent=stateContent, stateData=stateData, stateName=stateName)


@app.route('/world')
def worldPage():
    worldResponse = requests.get("https://api.covid19api.com/summary")
    worldjsonData = json.loads(worldResponse.content)

    countryData = {}
    countryDat = worldjsonData["Countries"]
    worldLen = len(worldjsonData["Countries"])
    for country in range(0, worldLen):
        countryData[str(countryDat[country]["CountryCode"])] = {}
        countryData[str(countryDat[country]["CountryCode"])]['name'] = countryDat[country]["Country"]

    worldDataResponse = requests.get("https://api.covid19api.com/summary")
    jsonResponse = json.loads(worldDataResponse.content)
    worldTotal = jsonResponse['Global']['TotalConfirmed']
    worldDeceased = jsonResponse['Global']['TotalDeaths']
    worldRecovered = jsonResponse['Global']['TotalRecovered']

    worldNewCases = jsonResponse['Global']['NewConfirmed']
    worldNewDeceases = jsonResponse['Global']['NewDeaths']
    worldNewRecovered = jsonResponse['Global']['NewRecovered']

    return render_template('world.html', worldTotal=worldTotal, worldNewCases=worldNewCases,
                           worldNewDeceases=worldNewDeceases, \
                           worldNewRecovered=worldNewRecovered, worldDeceased=worldDeceased,
                           worldRecovered=worldRecovered,
                           countryData=countryData)


@app.route('/world/<countryCode>')
def worldDataPage(countryCode):
    worldResponse = requests.get("https://api.covid19api.com/summary")
    worldjsonData = json.loads(worldResponse.content)
    worldlen = len(worldjsonData)

    countryNameData = {}
    countryDat = worldjsonData["Countries"]
    worldLen = len(worldjsonData["Countries"])
    for country in range(0, worldLen):
        countryNameData[str(countryDat[country]["CountryCode"])] = {}
        countryNameData[str(countryDat[country]["CountryCode"])]['name'] = countryDat[country]["Country"]

    countryData = {}
    worldLen = len(worldjsonData["Countries"])
    for country in range(0, worldLen):
        if str(worldjsonData["Countries"][country]["CountryCode"]) == countryCode:
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])] = {}
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['name'] = worldjsonData["Countries"][
                country].get('Country', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['TotalConfirmed'] = \
            worldjsonData["Countries"][country].get('TotalConfirmed', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['NewConfirmed'] = \
            worldjsonData["Countries"][country].get('NewConfirmed', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['TotalDeaths'] = \
            worldjsonData["Countries"][country].get('TotalDeaths', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['NewDeaths'] = \
            worldjsonData["Countries"][country].get('NewDeaths', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['TotalRecovered'] = \
            worldjsonData["Countries"][country].get('TotalRecovered', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['NewRecovered'] = \
            worldjsonData["Countries"][country].get('NewRecovered', None)
            countryData[str(worldjsonData["Countries"][country]["CountryCode"])]['date'] = worldjsonData["Countries"][
                country].get('Date', None)

    worldDataResponse = requests.get("https://api.covid19api.com/summary")
    jsonResponse = json.loads(worldDataResponse.content)
    worldTotal = jsonResponse['Global']['TotalConfirmed']
    worldDeceased = jsonResponse['Global']['TotalDeaths']
    worldRecovered = jsonResponse['Global']['TotalRecovered']

    worldNewCases = jsonResponse['Global']['NewConfirmed']
    worldNewDeceases = jsonResponse['Global']['NewDeaths']
    worldNewRecovered = jsonResponse['Global']['NewRecovered']

    return render_template('worldData.html', worldTotal=worldTotal, worldNewCases=worldNewCases,
                           worldNewDeceases=worldNewDeceases, \
                           worldNewRecovered=worldNewRecovered, worldDeceased=worldDeceased,
                           worldRecovered=worldRecovered,
                           countryData=countryData, countryCode=countryCode, countryNameData=countryNameData)


@app.route('/charts')
def chartHome():
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
    return render_template('charts.html', months=months)


@app.route('/charts/<month>')
def chartPage(month):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
    chartDataResponse = requests.get("https://api.covid19india.org/data.json")
    jsonData = json.loads(chartDataResponse.content)
    dateLen = len(jsonData['cases_time_series'])

    dates = []
    confirmed = []
    recovered = []
    deceased = []
    for dateData in range(0, dateLen):
        date = jsonData['cases_time_series'][dateData]['date']
        if month in date:
            dates.append(jsonData['cases_time_series'][dateData]['date'])
            confirmed.append(jsonData['cases_time_series'][dateData]['dailyconfirmed'])
            recovered.append(jsonData['cases_time_series'][dateData]['dailyrecovered'])
            deceased.append(jsonData['cases_time_series'][dateData]['dailydeceased'])
    legend = 'Confirmed'
    reclegend = 'Recovered'
    declegend = "Deceased"

    if month == "March":
        cMonth = '-03-'
    elif month == "April":
        cMonth = '-04-'
    elif month == "May":
        cMonth = '-05-'
    elif month == "June":
        cMonth = '-06-'
    elif month == "July":
        cMonth = '-07-'
    elif month == "August":
        cMonth = '-08-'
    elif month == "September":
        cMonth = '-09-'
    elif month == "October":
        cMonth = '-10-'
    labels = dates
    values = confirmed
    recvalues = recovered
    decvalues = deceased

    chartResponse = requests.get("https://api.rootnet.in/covid19-in/stats/testing/history")
    chartJson = json.loads(chartResponse.content)
    chartLen = len(chartJson['data'])

    chartDate = []
    sampleTest = []
    for day in range(0, chartLen):
        cDate = str(chartJson['data'][day]['day'])
        if cMonth in cDate:
            chartDate.append(str(chartJson['data'][day]['day']))
            sampleTest.append(chartJson['data'][day]['totalSamplesTested'])

    cLegend = 'Samples Tested'
    clabels = chartDate
    cvalues = sampleTest

    return render_template('chartData.html', values=values, labels=labels, legend=legend, \
                           recvalues=recvalues, reclegend=reclegend, declegend=declegend, decvalues=decvalues, \
                           month=month, cmonths=cMonth,months=months, cLegend=cLegend, clabels=clabels, cvalues=cvalues)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contact/submit', methods=['GET', 'POST'])
def contactSubmit():
    if request.method == 'POST':
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        mailaddress = request.form.get("mailaddress")
        subject = request.form.get("subject")
        feedback = {}
        feedback[mailaddress] = {}
        feedback[mailaddress]['firstname'] = firstname
        feedback[mailaddress]['lastname'] = lastname
        feedback[mailaddress]['mailaddress'] = mailaddress
        feedback[mailaddress]['subject'] = subject

        feedbackVal = json.dumps(feedback)

        with open('feedback.json') as json_file:
            data = json.load(json_file)
            temp = data['user_feedback']

            # python object to be appended
            feed = {"first_name": firstname,
                    "last_name": lastname,
                    "email": str(mailaddress),
                    "subject": subject
                    }
            temp.append(feed)

            write_json(data)
        flash("Submitted successfully.", "info")
        return render_template('contact.html')

    elif request.method == 'GET':
        return render_template('contact.html')


def write_json(data, filename='feedback.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/essentials', methods=['GET', 'POST'])
def essentials():
    if request.method == 'GET':
        essenRequest = requests.get('https://api.covid19india.org/resources/resources.json')
        essenResponse = json.loads(essenRequest.content)

        lenResp = len(essenResponse['resources'])
        stateJson = {}
        cityJson = {}
        for state in range(0, lenResp):
            stateJson[str(essenResponse['resources'][state]['state'])] = {}
            cityJson[str(essenResponse['resources'][state]['state'])] = []
        for stateVal in stateJson:
            state = str(stateVal)
            for city in range(0, lenResp):
                if state == str(essenResponse['resources'][city]['state']):
                    stateJson[state][str(essenResponse['resources'][city]['city'])] = {}
                    cityJson[state].append(str(essenResponse['resources'][city]['city']))
            cityJson[state] = list(set(cityJson[state]))
        return render_template('essentials.html', stateJson=stateJson, cityJson=cityJson)
    else:
        stateName = request.form.get("stateName")
        myCity = request.form.get("myCity")
        essenRequest = requests.get('https://api.covid19india.org/resources/resources.json')
        essenResponse = json.loads(essenRequest.content)

        lenResp = len(essenResponse['resources'])
        stateJson = {}
        cityJson = {}
        for state in range(0, lenResp):
            stateJson[str(essenResponse['resources'][state]['state'])] = {}
            cityJson[str(essenResponse['resources'][state]['state'])] = []
        for stateVal in stateJson:
            state = str(stateVal)
            for city in range(0, lenResp):
                if state == str(essenResponse['resources'][city]['state']):
                    stateJson[state][str(essenResponse['resources'][city]['city'])] = {}
                    cityJson[state].append(str(essenResponse['resources'][city]['city']))
            cityJson[state] = list(set(cityJson[state]))

        for stateVal in stateJson:
            state = str(stateVal)
            for city in stateJson[state]:
                for cityVal in range(0, lenResp):
                    if (state == str(essenResponse['resources'][cityVal]['state'])) and (
                            city == str(essenResponse['resources'][cityVal]['city'])):
                        stateJson[state][city][str(essenResponse['resources'][cityVal]['category'])] = {}

        for stateVal in stateJson:
            state = str(stateVal)
            for city in stateJson[state]:
                for category in stateJson[state][city]:
                    for cityVal in range(0, lenResp):
                        if (state == str(essenResponse['resources'][cityVal]['state'])) and (
                                city == str(essenResponse['resources'][cityVal]['city']) \
                                and (category == str(essenResponse['resources'][cityVal]['category']))):
                            stateJson[state][city][category][
                                str(essenResponse['resources'][cityVal]['nameoftheorganisation'])] = {}
                            stateJson[state][city][category][
                                str(essenResponse['resources'][cityVal]['nameoftheorganisation'])][
                                'descriptionandorserviceprovided'] = str(
                                essenResponse['resources'][cityVal]['descriptionandorserviceprovided'])
                            stateJson[state][city][category][
                                str(essenResponse['resources'][cityVal]['nameoftheorganisation'])]['contact'] = str(
                                essenResponse['resources'][cityVal]['contact'])
                            stateJson[state][city][category][
                                str(essenResponse['resources'][cityVal]['nameoftheorganisation'])]['phonenumber'] = str(
                                essenResponse['resources'][cityVal]['phonenumber'])

        finalOut = stateJson[stateName][myCity]
        return render_template('essentials.html', finalOut=finalOut, cityJson=cityJson, stateJson=stateJson,
                               state=stateName, city=myCity)


@app.route('/hospitals')
def hospitals():
    hospitalsData = requests.get("https://api.rootnet.in/covid19-in/hospitals/beds")
    hospitalsJson = json.loads(hospitalsData.content)

    ruralHospitals = str(hospitalsJson['data']['summary']['ruralHospitals'])
    ruralBeds = str(hospitalsJson['data']['summary']['ruralBeds'])
    urbanHospitals = str(hospitalsJson['data']['summary']['urbanHospitals'])
    urbanBeds = str(hospitalsJson['data']['summary']['urbanBeds'])
    totalHospitals = str(hospitalsJson['data']['summary']['totalHospitals'])
    totalBeds = str(hospitalsJson['data']['summary']['totalBeds'])

    source = str(hospitalsJson['data']['sources'][0]['url'])
    lastUpdated = str(hospitalsJson['data']['sources'][0]['lastUpdated'])

    lenResp = len(hospitalsJson['data']['regional'])
    stateJson = {}
    states = []
    for state in range(0, lenResp):
        states.append(str(hospitalsJson['data']['regional'][state]['state']))

    states.remove("INDIA")

    for state in range(0, lenResp):
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])] = {}
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['ruralHospitals'] = str(
            hospitalsJson['data']['regional'][state]['ruralHospitals'])
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['ruralBeds'] = str(
            hospitalsJson['data']['regional'][state]['ruralBeds'])
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['urbanHospitals'] = str(
            hospitalsJson['data']['regional'][state]['urbanHospitals'])
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['urbanBeds'] = str(
            hospitalsJson['data']['regional'][state]['urbanBeds'])
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['totalHospitals'] = str(
            hospitalsJson['data']['regional'][state]['totalHospitals'])
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['totalBeds'] = str(
            hospitalsJson['data']['regional'][state]['totalBeds'])
        stateJson[str(hospitalsJson['data']['regional'][state]['state'])]['asOn'] = str(
            hospitalsJson['data']['regional'][state]['asOn'])

    return render_template('hospitals.html', ruralHospitals=ruralHospitals, ruralBeds=ruralBeds,
                           urbanHospitals=urbanHospitals, \
                           urbanBeds=urbanBeds, totalHospitals=totalHospitals, totalBeds=totalBeds, source=source, \
                           lastUpdated=lastUpdated, states=states, stateJson=json.dumps(stateJson))


@app.route('/medicalColleges')
def medicalCollege():
    hospitalsData = requests.get("https://api.rootnet.in/covid19-in/hospitals/medical-colleges")
    hospitalsJson = json.loads(hospitalsData.content)

    lenResp = len(hospitalsJson['data']['medicalColleges'])
    states = []
    for state in range(0, lenResp):
        states.append(str(hospitalsJson['data']['medicalColleges'][state]['state']))
    states = set(states)
    lenResp = len(hospitalsJson['data']['medicalColleges'])
    stateJson = {}
    for state in range(0, lenResp):
        stateJson[str(hospitalsJson['data']['medicalColleges'][state]['state'])] = {}

    for stateVal in stateJson:
        stateN = str(stateVal)
        for stateName in range(0, lenResp):
            if stateN == str(hospitalsJson['data']['medicalColleges'][stateName]['state']):
                stateJson[stateN][str(hospitalsJson['data']['medicalColleges'][stateName]['name'])] = {}
                stateJson[stateN][str(hospitalsJson['data']['medicalColleges'][stateName]['name'])]['city'] = \
                hospitalsJson['data']['medicalColleges'][stateName]['city']
                stateJson[stateN][str(hospitalsJson['data']['medicalColleges'][stateName]['name'])]['ownership'] = \
                hospitalsJson['data']['medicalColleges'][stateName]['ownership']
                stateJson[stateN][str(hospitalsJson['data']['medicalColleges'][stateName]['name'])][
                    'admissionCapacity'] = hospitalsJson['data']['medicalColleges'][stateName]['admissionCapacity']
                stateJson[stateN][str(hospitalsJson['data']['medicalColleges'][stateName]['name'])]['hospitalBeds'] = \
                hospitalsJson['data']['medicalColleges'][stateName]['hospitalBeds']

    return render_template('medicalColleges.html', states=states, stateJson=json.dumps(stateJson))


@app.route('/helpline')
def helpline():
    helpLineData = requests.get("https://api.rootnet.in/covid19-in/contacts")
    helpLineJson = json.loads(helpLineData.content)

    lenResp = len(helpLineJson['data']['contacts']['regional'])
    stateData = {}

    primaryNo = helpLineJson['data']['contacts']['primary']['number']
    tollFree = helpLineJson['data']['contacts']['primary']['number-tollfree']
    email = helpLineJson['data']['contacts']['primary']['email']
    twitter = helpLineJson['data']['contacts']['primary']['twitter']
    facebook = helpLineJson['data']['contacts']['primary']['facebook']

    for state in range(0, lenResp):
        stateData[str(helpLineJson['data']['contacts']['regional'][state]['loc'])] = {}
        stateData[str(helpLineJson['data']['contacts']['regional'][state]['loc'])]['number'] = \
        helpLineJson['data']['contacts']['regional'][state]['number']

    return render_template('helpline.html', stateData=stateData, primaryNo=primaryNo, tollFree=tollFree, email=email, \
                           twitter=twitter, facebook=facebook)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/kerala')
def kerala():
    keralaData = requests.get("https://keralastats.coronasafe.live/summary.json")
    keralaJson = json.loads(keralaData.content)

    keralaSummary = keralaJson['summary']
    keralaDelta= keralaJson['delta']

    klConfirmed = keralaSummary['confirmed']
    klRecovered = keralaSummary['recovered']
    klDeceased = keralaSummary['deceased']
    klActive = keralaSummary['active']

    klDeltaConfirmed = keralaDelta['confirmed']
    klDeltaRecovered = keralaDelta['recovered']
    klDeltaDeceased = keralaDelta['deceased']
    klDeltaActive = keralaDelta['active']

    lastUpdated = keralaJson['last_updated']

    keralaData1 = requests.get("https://keralastats.coronasafe.live/testreports.json")
    keralaSampleJson = json.loads(keralaData1.content)

    keralaSampleLen = len(keralaSampleJson['reports'])
    klLatestSampleData = keralaSampleJson['reports'][keralaSampleLen-1]

    totalSampleTested = klLatestSampleData['total']
    totalSampleTestedToday = klLatestSampleData['today']
    totalSampleTestedPositive = klLatestSampleData['positive']
    totalSampleTestedPositiveToday = klLatestSampleData['today_positive']

    return render_template('kerala.html',klConfirmed=klConfirmed,klRecovered=klRecovered,klDeceased=klDeceased,\
                           klActive=klActive,klDeltaConfirmed=klDeltaConfirmed,klDeltaRecovered=klDeltaRecovered,\
                           klDeltaDeceased=klDeltaDeceased,klDeltaActive=klDeltaActive,lastUpdated=lastUpdated,\
                           totalSampleTested=totalSampleTested,totalSampleTestedToday=totalSampleTestedToday,\
                           totalSampleTestedPositive=totalSampleTestedPositive,totalSampleTestedPositiveToday=totalSampleTestedPositiveToday)


@app.route('/kerala/districts')
def keralaDistricts():
    keralaData = requests.get("https://keralastats.coronasafe.live/histories.json")
    keralaDistJson = json.loads(keralaData.content)

    keralaDistLen = len(keralaDistJson['histories'])
    klLatestDistData = keralaDistJson['histories'][keralaDistLen - 1]['summary']

    klDeltaDistData = keralaDistJson['histories'][keralaDistLen - 1]['delta']

    districtData = {}
    for district in klLatestDistData:
        districtData[district] ={}
        districtData[district]['confirmed'] = klLatestDistData[district]['confirmed']
        districtData[district]['active'] = klLatestDistData[district]['active']
        districtData[district]['recovered'] = klLatestDistData[district]['recovered']
        districtData[district]['deceased'] = klLatestDistData[district]['deceased']
        districtData[district]['under_observation'] = klLatestDistData[district]['total_obs']
        districtData[district]['hospital_isolation'] = klLatestDistData[district]['hospital_obs']
        districtData[district]['home_isolation'] = klLatestDistData[district]['home_obs']
        districtData[district]['hospitalized_today'] = klLatestDistData[district]['hospital_today']

    for district in klDeltaDistData:
        districtData[district]['deltaConfirmed'] = klDeltaDistData[district]['confirmed']
        districtData[district]['deltaActive'] = klDeltaDistData[district]['active']
        districtData[district]['deltaRecovered'] = klDeltaDistData[district]['recovered']
        districtData[district]['deltaDeceased'] = klDeltaDistData[district]['deceased']
        districtData[district]['deltaUnder_observation'] = klDeltaDistData[district]['total_obs']
        districtData[district]['deltaHospital_isolation'] = klDeltaDistData[district]['hospital_obs']
        districtData[district]['deltaHome_isolation'] = klDeltaDistData[district]['home_obs']
        districtData[district]['deltaHospitalized_today'] = klDeltaDistData[district]['hospital_today']

    lastUpdate = keralaDistJson['last_updated']

    return render_template('districts.html',districtData=districtData,lastUpdate=lastUpdate)


@app.route('/kerala/containmentZones')
def keralaContainmentZones():
    keralaData = requests.get("https://keralastats.coronasafe.live/hotspots.json")
    keralaZoneJson = json.loads(keralaData.content)

    klLatestZoneData = keralaZoneJson['hotspots']

    districtData = {}
    for district in klLatestZoneData:
        distName =district['district']
        districtData[distName] = {}

    for district in districtData:
        for district1 in klLatestZoneData:
            distName = district1['district']
            lsgd = district1['lsgd']
            if district == distName:
                districtData[district][lsgd] = []

    for district in districtData:
        for district1 in klLatestZoneData:
            distName = district1['district']
            lsgd = district1['lsgd']
            if district == distName:
                wards = district1['wards']
                wardsData = wards.split(",")
                for value in wardsData:
                    if "(SubWards)" in value:
                        print(value)
                        value = value.replace("(SubWards)","")
                    else:
                        None
                    districtData[district][lsgd].append(remove(value))
                    districtData[district][lsgd].sort(key=natural_keys)
    return districtData


# main driver function
if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=5000,threaded=True)
    app.run(debug=True)
