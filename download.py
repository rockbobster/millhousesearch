import requests
import re

#Rightmove Regions
#Somerset,Dorset,Wiltshire,Devon
#rmRegion=["REGION%5E61322","REGION%5E61298","REGION%5E61328","REGION%5E61297"]

rmRegion=["REGION%5E61297"]


baseurl='http://www.rightmove.co.uk/property-for-sale/find.html?'
baseurl += '&maxPrice=250000'
baseurl += '&propertyTypes=detached'
baseurl += '&maxDaysSinceAdded=14'

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'})

for region in rmRegion:
    #append specific region and page number for page 1 of region
    url = baseurl + '&locationIdentifier=' + region + '&index=0'
    response = session.get(url)

    #Find number of properties
    p = re.compile("\<span class\=\"searchHeader-resultCount\" data-bind\=\"counter: resultCount, formatter: numberFormatter\"\>(\d+)\<\/span\>")
    m = p.search(str(response.content))
    recCount = int(m.group(1))
    propIDList=[]


    for page in range(0,recCount,24):
        url = baseurl + '&locationIdentifier=' + region + '&index=' + str(page)
        response = session.get(url)

        p = re.compile("\<a id\=\"prop(\d\d+)\" class\=\"propertyCard-anchor")
        resultSet = p.finditer(str(response.content))
        next(resultSet) #Skip first 'featured property' - not a real result

        for result in resultSet:
            propIDList.append(result.group(1))

    for prop in propIDList:
        print(prop)
        print(propIDList[int(prop)])



#http://www.rightmove.co.uk/property-for-sale/property-51283944.html

#print(session.headers)
#print(response.headers)
#print(response.status_code)
#print(pages)

        #f = open('workfile.html', 'w')
#f.write(str(response.content))
#f.close()