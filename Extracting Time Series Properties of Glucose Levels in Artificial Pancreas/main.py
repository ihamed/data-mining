import pandas as pd
from datetime import datetime
import math
import datetime as d

#read used columns
data = pd.read_csv (r'CGMData.csv', usecols=[1,2,30])

#read to get auto mode threeshold
insulin = pd.read_csv (r'InsulinData.csv', usecols=[1,2,16])

threeshold = insulin[insulin['Alarm']=='AUTO MODE ACTIVE PLGM OFF'].index.values[-1]
threesholdTime = datetime.strptime(insulin['Time'][threeshold], '%H:%M:%S').time()
threesholdDate= d.datetime.strptime(insulin['Date'][threeshold], '%m/%d/%Y')
#print(insulin['Date'][threeshold])

startDayTime = d.time(6,0,0)
endDayTime = d.time(23, 59, 59)
startOverNight = d.time(0, 0, 1)
endOverNight = d.time(5, 59, 59)

length = len(data)
eleminated_dates = []
countDays = 0
i = length - 1
countManualDays = 0
while i > 0:
    date = data['Date'][i]
    countData = 0
    countTime = 0
    countDays += 1
    while date == data['Date'][i]:
        if not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
            countData+=1
        countTime = countTime + 1
        if i > 0:
            i = i - 1
        else:
            break
    #print (date , " -> ", countTime , " data ->", countData," ", (countData / 288)*100,"%")
    if (countData / 288) *100 < 80:
        eleminated_dates.append(date)
    elif(countData / 288) *100 > 100:
        eleminated_dates.append(date)
    if d.datetime.strptime(date, '%m/%d/%Y') < threesholdDate:
        countManualDays += 1
        #print(data['Date'][i])

        

##manual
hyperglycemia = {'daytime':0,'overnight':0}
hyperglycemiaCritical = {'daytime':0,'overnight':0}
range = {'daytime':0,'overnight':0}
rangeSecondary = {'daytime':0,'overnight':0}
hypoglycemiaLevelOne = {'daytime':0,'overnight':0}
hypoglycemiaLevelTwo = {'daytime':0,'overnight':0}
ManualDate = 0

def segmant_daytime(val):
    global hyperglycemia
    global hyperglycemiaCritical
    global range
    global rangeSecondary
    global hypoglycemiaLevelOne
    global hypoglycemiaLevelTwo
    global ManualDate
    ManualDate += 1
    if val > 250:
        hyperglycemiaCritical['daytime'] += 1
    if val > 180:
        hyperglycemia['daytime'] += 1
    if val >= 70 and val <= 180:
        range['daytime'] += 1
    if val >=70 and val <=150:
        rangeSecondary['daytime'] += 1
    if val < 70:
        hypoglycemiaLevelOne['daytime'] += 1
    if val < 54:
        hypoglycemiaLevelTwo['daytime'] += 1


def segmant_overnight(val):
    global hyperglycemia
    global hyperglycemiaCritical
    global range
    global rangeSecondary
    global hypoglycemiaLevelOne
    global hypoglycemiaLevelTwo
    global ManualDate

    ManualDate += 1
    if val > 250:
        hyperglycemiaCritical['overnight'] += 1
    if val > 180:
        hyperglycemia['overnight'] += 1
    if val >= 70 and val <= 180:
        range['overnight'] += 1
    if val >=70 and val <=150:
        rangeSecondary['overnight'] += 1
    if val < 70:
        hypoglycemiaLevelOne['overnight'] += 1
    if val < 54:
        hypoglycemiaLevelTwo['overnight'] += 1

##auto
auto_hyperglycemia = {'daytime':0,'overnight':0}
auto_hyperglycemiaCritical = {'daytime':0,'overnight':0}
auto_range = {'daytime':0,'overnight':0}
auto_rangeSecondary = {'daytime':0,'overnight':0}
auto_hypoglycemiaLevelOne = {'daytime':0,'overnight':0}
auto_hypoglycemiaLevelTwo = {'daytime':0,'overnight':0}
AutoData = 0
def auto_segmant_daytime(val):
    global auto_hyperglycemia
    global auto_hyperglycemiaCritical
    global auto_range
    global auto_rangeSecondary
    global auto_hypoglycemiaLevelOne
    global auto_hypoglycemiaLevelTwo
    global AutoData

    AutoData+=1
    if val > 250:
        auto_hyperglycemiaCritical['daytime'] += 1
    if val > 180:
        auto_hyperglycemia['daytime'] += 1
    if val >= 70 and val <= 180:
        auto_range['daytime'] += 1
    if val >=70 and val <=150:
        auto_rangeSecondary['daytime'] += 1
    if val < 70:
        auto_hypoglycemiaLevelOne['daytime'] += 1
    if val < 54:
        auto_hypoglycemiaLevelTwo['daytime'] += 1


def auto_segmant_overnight(val):
    global auto_hyperglycemia
    global auto_hyperglycemiaCritical
    global auto_range
    global auto_rangeSecondary
    global auto_hypoglycemiaLevelOne
    global auto_hypoglycemiaLevelTwo
    global AutoData

    AutoData+=1
    if val > 250:
        auto_hyperglycemiaCritical['overnight'] += 1
    if val > 180:
        auto_hyperglycemia['overnight'] += 1
    if val >= 70 and val <= 180:
        auto_range['overnight'] += 1
    if val >=70 and val <=150:
        auto_rangeSecondary['overnight'] += 1
    if val < 70:
        auto_hypoglycemiaLevelOne['overnight'] += 1
    if val < 54:
        auto_hypoglycemiaLevelTwo['overnight'] += 1

#loop to get the sum of segmants auto - manual in periods

i = length - 1
while i > 0:
    date =  data['Date'][i]
    if date in eleminated_dates:
        i -= 1
        continue
    while date == data['Date'][i]:
        time = datetime.strptime(data['Time'][i], '%H:%M:%S').time()
        #print(time, "----->  ", threesholdTime)
        if d.datetime.strptime(date, '%m/%d/%Y') < threesholdDate:# check if it is manual or auto  and time < threesholdTime
            #print(date, " time:", time, " val: ", data['Sensor Glucose (mg/dL)'][i])
            if time >= startDayTime and time <= endDayTime and not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                segmant_daytime(data['Sensor Glucose (mg/dL)'][i])
                #print("Manual -> day time : ", time)
            elif time >= startOverNight and time <= endOverNight and not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                segmant_overnight(data['Sensor Glucose (mg/dL)'][i])
                #print("Manual -> Over Night : ", time)
        elif d.datetime.strptime(date, '%m/%d/%Y') == threesholdDate and time < threesholdTime:
            if time >= startDayTime and time <= endDayTime and not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                segmant_daytime(data['Sensor Glucose (mg/dL)'][i])
                #print("EQUAL Manual  -> day time : ", time)
            elif time >= startOverNight and time <= endOverNight and not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                segmant_overnight(data['Sensor Glucose (mg/dL)'][i])
                #print("EQUAL Manual -> over night : ", time)
        else:
            if time >= startDayTime and time <= endDayTime and not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                auto_segmant_daytime(data['Sensor Glucose (mg/dL)'][i])
                #print("auto -> day time : ", time)
            elif time >= startOverNight and time <= endOverNight and not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                auto_segmant_overnight(data['Sensor Glucose (mg/dL)'][i])
                #print("auto -> over night : ", time)
        if i > 0:
            i = i - 1
        else:
            break
countAutoDays = countDays - countManualDays
print ('manaul: ', countManualDays, 'auto: ', countDays-countManualDays)
print ("hyperglycemia: ", hyperglycemia, "hyperglycemiaCritical: ", hyperglycemiaCritical, "range: ", range, "rangeSecondary: ", rangeSecondary, "hypoglycemiaLevelOne: ",hypoglycemiaLevelOne, "hypoglycemiaLevelTwo: ",hypoglycemiaLevelTwo )
print ("auto_hyperglycemia: ", auto_hyperglycemia, "auto_hyperglycemiaCritical: ", auto_hyperglycemiaCritical, "auto_range: ", auto_range, "auto_rangeSecondary: ", auto_rangeSecondary, "auto_hypoglycemiaLevelOne: ",auto_hypoglycemiaLevelOne, "auto_hypoglycemiaLevelTwo: ",auto_hypoglycemiaLevelTwo )

hyperglycemia.update((x, (y/(288*countManualDays))*100) for x, y in hyperglycemia.items())
hyperglycemiaCritical.update((x, (y/(288*countManualDays))*100) for x, y in hyperglycemiaCritical.items())
range.update((x, (y/(288*countManualDays))*100) for x, y in range.items())
rangeSecondary.update((x, (y/(288*countManualDays))*100) for x, y in rangeSecondary.items())
hypoglycemiaLevelOne.update((x, (y/(288*countManualDays))*100) for x, y in hypoglycemiaLevelOne.items())
hypoglycemiaLevelTwo.update((x, (y/(288*countManualDays))*100) for x, y in hypoglycemiaLevelTwo.items())

auto_hyperglycemia.update((x, (y/(288*countAutoDays))*100) for x, y in auto_hyperglycemia.items())
auto_hyperglycemiaCritical.update((x, (y/(288*countAutoDays))*100) for x, y in auto_hyperglycemiaCritical.items())
auto_range.update((x, (y/(288*countAutoDays))*100) for x, y in auto_range.items())
auto_rangeSecondary.update((x, (y/(288*countAutoDays))*100) for x, y in auto_rangeSecondary.items())
auto_hypoglycemiaLevelOne.update((x, (y/(288*countAutoDays))*100) for x, y in auto_hypoglycemiaLevelOne.items())
auto_hypoglycemiaLevelTwo.update((x, (y/(288*countAutoDays))*100) for x, y in auto_hypoglycemiaLevelTwo.items())

# write into csv file
#list of output
hyperglycemia_list = [hyperglycemia['overnight'], auto_hyperglycemia['overnight']]
hyperglycemiaCritical_list = [hyperglycemiaCritical['overnight'], auto_hyperglycemiaCritical['overnight']]
range_list = [range['overnight'], auto_range['overnight']]
rangeSecondary_list = [rangeSecondary['overnight'], auto_rangeSecondary['overnight']]
hypoglycemiaLevelOne_list = [hypoglycemiaLevelOne['overnight'], auto_hypoglycemiaLevelOne['overnight']]
hypoglycemiaLevelTwo_list = [hypoglycemiaLevelTwo['overnight'], auto_hypoglycemiaLevelTwo['overnight']]
#daytime
hyperglycemia_list_daytime = [hyperglycemia['daytime'], auto_hyperglycemia['daytime']]
hyperglycemiaCritical_list_daytime = [hyperglycemiaCritical['daytime'], auto_hyperglycemiaCritical['daytime']]
range_list_daytime = [range['daytime'], auto_range['daytime']]
rangeSecondary_list_daytime = [rangeSecondary['daytime'], auto_rangeSecondary['daytime']]
hypoglycemiaLevelOne_list_daytime = [hypoglycemiaLevelOne['daytime'], auto_hypoglycemiaLevelOne['daytime']]
hypoglycemiaLevelTwo_list_daytime = [hypoglycemiaLevelTwo['daytime'], auto_hypoglycemiaLevelTwo['daytime']]
#full day
hyperglycemia_list_day = [(hyperglycemia['daytime']+hyperglycemia['overnight'])/2, (auto_hyperglycemia['daytime']+auto_hyperglycemia['daytime'])/2]
hyperglycemiaCritical_list_day = [(hyperglycemiaCritical['daytime']+hyperglycemiaCritical['overnight'])/2, (auto_hyperglycemiaCritical['daytime']+auto_hyperglycemiaCritical['overnight'])/2]
range_list_day = [(range['daytime']+range['overnight'])/2, (auto_range['daytime']+auto_range['overnight'])/2]
rangeSecondary_list_day = [(rangeSecondary['daytime']+rangeSecondary['overnight'])/2, (auto_rangeSecondary['daytime']+auto_rangeSecondary['overnight'])/2]
hypoglycemiaLevelOne_list_day = [(hypoglycemiaLevelOne['daytime']+hypoglycemiaLevelOne['overnight'])/2, (auto_hypoglycemiaLevelOne['daytime']+auto_hypoglycemiaLevelOne['overnight'])/2]
hypoglycemiaLevelTwo_list_day = [(hypoglycemiaLevelTwo['daytime']+hypoglycemiaLevelTwo['overnight'])/2, (auto_hypoglycemiaLevelTwo['daytime']+auto_hypoglycemiaLevelTwo['overnight'])/2]


dataDic = {"hyperglycemia_list":hyperglycemia_list,"hyperglycemiaCritical_list":hyperglycemiaCritical_list, "range_list":range_list, "rangeSecondary_list":rangeSecondary_list
           ,"hypoglycemiaLevelOne_list":hypoglycemiaLevelOne_list, "hypoglycemiaLevelTwo_list":hypoglycemiaLevelTwo_list,
           "hyperglycemia_list_daytime":hyperglycemia_list_daytime,"hyperglycemiaCritical_list_daytime":hyperglycemiaCritical_list_daytime, "range_list_daytime":range_list_daytime, "rangeSecondary_list_daytime":rangeSecondary_list_daytime
           ,"hypoglycemiaLevelOne_list_daytime":hypoglycemiaLevelOne_list_daytime, "hypoglycemiaLevelTwo_list_daytime":hypoglycemiaLevelTwo_list_daytime,
           "hyperglycemia_list_day":hyperglycemia_list_day,"hyperglycemiaCritical_list_day":hyperglycemiaCritical_list_day, "range_list_day":range_list_day, "rangeSecondary_list_day":rangeSecondary_list_day
           ,"hypoglycemiaLevelOne_list_day":hypoglycemiaLevelOne_list_day, "hypoglycemiaLevelTwo_list_day":hypoglycemiaLevelTwo_list_day
           }
result = pd.DataFrame(dataDic)
result.to_csv('Results.csv', header=False, index=False)


