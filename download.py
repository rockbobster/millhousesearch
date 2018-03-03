import requests
import re
import mysql.connector

#Rightmove Regions
rmRegion=([["REGION%5E61297","Devon"],
           ["REGION%5E61322","Somerset"],
           ["REGION%5E61298","Dorset"],
           ["REGION%5E61328","Wiltshire"]])


baseurl='http://www.rightmove.co.uk/property-for-sale/find.html?'
baseurl += '&maxPrice=150000'
baseurl += '&propertyTypes=detached'
baseurl += '&maxDaysSinceAdded=14'

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'})

for region,county in rmRegion:
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

    #Create mySQL connector and base insert string
    cnx = mysql.connector.connect(user='scrapper', password='!Nsert23', host='127.0.0.1', database='property')
    cursor = cnx.cursor()
    addProp = ("INSERT INTO property.houses "
               "(reseller,EA,url,county,postcode,latitude,longitude,propertyID,propertyType,propertySubType,price,beds,dateAdded) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    # Loop over each property to download full details
    for prop in propIDList:

        # Download the property details page for prop
        url='http://www.rightmove.co.uk/property-for-sale/property-' + prop + '.html'
        response = str(session.get(url).content)

        # Strip out the short and long decscription
        shortDesc = re.search("\<title\>([\w \,]+)\<\/title\>",response).group(1)
        fullDesc = re.search("\<p itemprop=\"description\"\>(.+?)\<\/p\>",response).group(1)
        EA = re.search("companyName\":\"(.+?)\"",response).group(1)

        # Grab substring containing key data
        propdetails = re.search("{\"location\":{(.+)selectedCurrency",response).group(1)

        # Now examine the substring and get that data
        postcode = re.search("postcode\":\"(\w+ \w+)\"",propdetails).group(1)
        latitude = re.search("latitude\":([-\d\.]+)",propdetails).group(1)
        longitude = re.search("longitude\":([-\d\.]+)", propdetails).group(1)
        propertyID = re.search("propertyId\":([\d]+)", propdetails).group(1)
        propertyType = re.search("propertyType\":\"([\w]+)", propdetails).group(1)
        propertySubType = re.search("propertySubType\":\"([\w]+)", propdetails).group(1)
        price = re.search("price\":([\d\.]+)", propdetails).group(1)
        beds = re.search("beds\":([\d]+)", propdetails).group(1)
        dateAdded = re.search("added\":\"([\d]+)", propdetails).group(1)

        cursor.execute(addProp,('Rightmove',EA,url,county,postcode,latitude,longitude,propertyID,propertyType,propertySubType,price,beds,dateAdded))
        cnx.commit()


    cursor.close()
    cnx.close()



#print(session.headers)
#print(response.headers)
#print(response.status_code)
#print(pages)

#{"location":
#{"postcode":"EX20 2DE","country":"GB","latitude":50.80104270685834,"longitude":-3.89710189589049}
        # ,"propertyId":49215366,"viewType":"Current","imageCount":9,"floorplanCount":1,"videoProvider":"Embedded","propertyInfo":
        # {"propertyType":"Houses","propertySubType":"Cottage","price":189995.0,"beds":3,"added":"20170706","soldSTC":false,"retirement":null,"preOwned":"Resale","ownership":"Non-shared ownership","auctionOnly":false,"letAgreed":false,"lettingType":null,"furnishedType":null,"minSizeFt":null,"maxSizeFt":null,"minSizeAc":null,"maxSizeAc":null,"businessForSale":false,"priceQualifier":"Offers in Region of","currency":"GBP","selectedPrice":null,"selectedCurrency":null
        # }
        # }

#f = open(prop + '.html', 'w')
#f.write(response)
#f.close()