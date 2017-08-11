import requests as r
from bs4 import BeautifulSoup as bs
import time
from urllib.parse import urljoin
from os import getcwd, path


url = "http://metallurgy-metalworking.europages.co.uk/companies/Steels%20and%20metals%20-%20machining.html"
headers = {}
params = {}
to = 5

cwd = getcwd()


relevantLinks = []
nextPageUrl = url#"http://metallurgy-metalworking.europages.co.uk/companies/pg-56/Steels%20and%20metals%20-%20machining.html"
lastSoup = None
lastPage = []
v = 1;

def valid(url):
    validurl = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if len(validurl.findall(url))!=0:
        return True
    else:
        return False

def getAll(start = url, v=1):
    global lastPage, nextPageUrl
    if not valid(start):
        print("Invalid url %s" % start)
        return
    
    retries = 1
    prev = ""
    
    while True:
        pageEmails = []
        if nextPageUrl!="":
            prev = nextPageUrl;
            retries = 1
        nextPageUrl = getCompanyLinks(prev)
        try:
            pageNumber = prev.split("/pg-")[1].split("/")[0]
        except:
            pageNumber = "1"
        if path.isfile(getcwd()+"\\emails\\page%s.txt"%(pageNumber)):
            print("✔File exists, skip page.")
            continue
        if len(lastPage)!=0:
            hp = []
            for i in lastPage:
                print()
                try:
                    hp = getHomepageAndKeys(i)
                except:
                    print("  ✘ Europages error")
                try:
                    e = getEmail(hp[0])
                    if e!=None:
                        for emailAddress in set(e):
                            if "javascript" not in emailAddress:
                                ema = emailAddress.split("?")[0]+";%s"%";".join(hp)
                                pageEmails.append(ema)
                            else:
                                print("  ✘ Scrambled email")
                        print("  "+str(set(e)))
                except:
                    print("  ✘ Homepage error")
            print("  This page got us %s emails: %s"%(len(pageEmails), str(pageEmails)))
            if len(pageEmails)>0:
                fn = "emails\\page%s.txt"%(pageNumber)
                file = open(fn, 'w', encoding='utf8')
                x = file.write("email;site;headcount;salesstaff;export\n")
                for i in pageEmails:
                    x=file.write(i.strip()+"\n")
                file.close()
                print("✔File saved (%s)"%fn)
                
        
        if nextPageUrl == "":
            if lastSoup=="None":
                print("✘ Internet connection error (%s)"%retries)
                retries+=1
                if retries>5:
                    break
                time.sleep(5)
                continue
            if "Europages - Service temporarely unavailable" in lastSoup.find('title').contents:
                if v: print("✘ Error 500 (%s)"%retries)
                retries+=1
                if retries>49:
                    if v: print("✘ Retry limit. 15 sec, one last time")
                    time.sleep(15)
                if retries>50:
                    if v: print("✘ Finished with error page")
                    break
                time.sleep(5)
            else:
                if v: print("✔ Not the error page. Must be finished. Page title is: " + lastSoup.find('title'))
                break

                

def getCompanyLinks(currentUrl, v=1):
    if not valid(currentUrl):
        print("Invalid url %s" % currentUrl)
        return
    global relevantLinks, lastSoup, lastPage
    lastPage = []
    if v: print("\nPage %s"%currentUrl)
    try:
        result = r.get(currentUrl, headers=headers, params=params, timeout=to)
    except:
        print("✘  timeout")
        return ""
    soup = bs(result.text, "html.parser")
    lastSoup = soup
    result.close()

    links = soup.find_all('a')
    
    companyClass = {'company-name', 'display-spinner'}
    nextClass = {'prevnext', 'btn-next', 'display-spinner'}
    returnUrl = ""

    howMany = 0
    
    for link in links:
            linkRawClass = link.get('class')
            if linkRawClass == None:
                continue
            linkClass = set(linkRawClass)
            if linkClass == companyClass:
                relevantLinks.append(link.get('href'))
                lastPage.append(link.get('href'))
                howMany+=1
            if linkClass == nextClass:
                returnUrl = link.get('href')
    if v:
        if howMany>0: print("✔ %s companies"%str(howMany))
        else: print("✘ %s companies"%str(howMany))
    return returnUrl

homepages = []

def getHomepageAndKeys(europagesUrl, v=1):
    if not valid(europagesUrl):
        print("Invalid url %s" % europagesUrl)
        return
    global lastSoup, homepages
    retries = 1
    while retries<3:
        homePageLink = ""
        keyPeople = ""
        salesStaff = ""
        exportSales = ""
        try:
            result = r.get(europagesUrl, timeout=to)
        except:
            print("✘  timeout")
            retries+=1
            continue
        soup = bs(result.text, "html.parser")
        lastSoup = soup
        result.close()

        links = soup.find_all('a')
        divs = soup.find_all('div')
        
        for link in links:
            lrc = link.get('class')
            if lrc == None: continue
            linkClass = set(lrc)
            if linkClass == {'button', 'compUrl'}:
                homePageLink = link.get('href')
                if v: print("  ✔ Homepage link: %s"%homePageLink)
                break
        for div in divs:
            lrc = div.get('class')
            if lrc == None: continue
            divClass = set(lrc)
            if divClass == {'data', 'sprite', 'icon-key-people'}:
                keyPeople = div.contents[0].replace("–", "-")
                if v: print("  ✔ Company headcount: %s"%keyPeople)
            if divClass == {'data', 'sprite', 'icon-key-sales'}:
                salesStaff = div.contents[0].replace("–", "-")
                if v: print("  ✔ Sales staff: %s"%salesStaff)
            if divClass == {'data', 'sprite', 'icon-key-export'}:
                exportSales = div.contents[0].replace("–", "-")
                if v: print("  ✔ Export sales: %s"%exportSales)
                                
        if homePageLink == "":
            if v: print("  ✘ Homepage link (%s)"%str(retries))
            time.sleep(5)
            retries+=1
            continue
        if keyPeople == "":
            if v: print("  ✘ Company headcount")
        if salesStaff == "":
            if v: print("  ✘ Sales staff")
        if exportSales == "":
            if v: print("  ✘ Export sales")
        
        homepages.append([homePageLink, keyPeople, salesStaff, exportSales])
        break
    return [homePageLink, keyPeople, salesStaff, exportSales]

def getHomepage(europagesUrl, v=1):
    if not valid(europagesUrl):
        print("Invalid url %s" % europagesUrl)
        return
    global lastSoup, homepages
    retries = 1
    while retries<3:
        homePageLink = ""
        try:
            result = r.get(europagesUrl, timeout=to)
        except:
            print("✘  timeout")
            retries+=1
            continue
        soup = bs(result.text, "html.parser")
        lastSoup = soup
        result.close()

        links = soup.find_all('a')
        for link in links:
            lrc = link.get('class')
            if lrc == None: continue
            linkClass = set(lrc)
            if linkClass == {'button', 'compUrl'}:
                homePageLink = link.get('href')
                if v: print("  ✔ Homepage link: %s"%homePageLink)
                homepages.append(homePageLink)
                break
        if homePageLink == "":
            if v: print("  ✘ Homepage link (%s)"%str(retries))
            time.sleep(5)
            retries+=1
            continue
        break
    return homePageLink

def getHomepages(urls):
    for url in urls:
        getHomepage(url,0)

contactWords = {'kontakt', 'temas', 'xiriirka', 'קאָנטאַקט', 'contact',
               'whakapā', 'կապ', 'tiếp xúc', 'தொடர்பு', 'ទំនាក់ទំនង',
               'кантакт', 'పరిచయం', 'холбоо барих', 'kọntaktị',
               'hafðu samband', 'lamba', 'kontakta', 'კონტაქტი',
               'اتصل', 'ການຕິດຕໍ່', 'ထိတှေ့', 'hubungan', 'makipag-ugnay',
               'contato', '聯繫', 'kontaktua', 'wasiliana', 'olubasọrọ',
               'ikopanya', 'əlaqə', 'ottaa yhteyttä', 'kontak', '접촉',
               'susisiekti', 'teagmháil', 'fifandraisana', 'අමතන්න',
               'kapcsolatba lépni', 'सम्पर्क', 'איש קשר', 'тамос', 'ਸੰਪਰਕ ਕਰੋ',
               'संपर्क साधा', 'контакт', 'aloqa', 'cysylltu', 'hubungi',
               'kontaktu', 'байланыс', 'oxhumana naye', 'संपर्क करें', '接触',
               'ബന്ധപ്പെടുക', 'kuntatt', 'kukhudzana', 'تماس', 'stik',
               'contacte', 'ติดต่อ', '联系', 'ಸಂಪರ್ಕ', 'સંપર્ક કરો', 'contatto',
               'رابطہ', 'যোগাযোগ', 'επικοινωνία', 'contacto', 'contatti'}

emails = []
allemails = []
company = ['http://www.minuteriebaitelli.it/mb', 'http://www.deltafluid.fr/', 'http://www.gbmlavorazioni.it', 'http://www.martin-joseph.com/', 'http://www.minuteriebaitelli.it/mb', 'http://www.rokvelas.lt/en/index', 'http://kera-industry.com/en/', 'http://www.temponi.it', 'http://www.kvt-fastening.de', 'http://www.ampo.fr', 'http://www.gpmcn.com/index.php?lang=en', 'http://ky.to/www.inductoheat.eu', 'http://www.cavalettospa.com', 'http://adiamix.com/', 'http://www.multiform.fr', 'http://www.cmi-meca.fr/', 'http://www.cnclebrun.com/spip.php?page=sommaireGB', 'http://www.dbn.fr/web/index.php?lang=UK', 'http://www.calip-group.fr/1.accueil?lang=en', 'http://www.sotraban.com/HAG-TECH.htm', 'http://adr-usinage.fr/', 'http://www.obein.com', 'http://www.torneriaserra.it', 'http://www.amco-metall.de', 'http://www.agtos.de/', 'http://www.aetztechnik-herz.de', 'http://www.energietechnik-essen.de ', 'http://www.s-m-f.de', 'http://www.stopa.com', 'http://www.theis.de/', 'http://www.hfp-bandstahl.de']

import re

def getEmails(urls):
    
    global emails, allemails
    for url in urls:
        getEmail(url.strip())
    emails = list(set(emails))
    allemails = list(set(allemails))
    file = open("emails.txt", 'w')
    for i in emails:
        file.write(i+"\n")
    file.close()
    print("✔ Kirjutasin faili emails.txt %s emaili"%str(len(emails)))
    

def getEmail(companyUrl, v=0):
    if not valid(companyUrl):
        print("  ✘ Invalid url %s" % companyUrl)
        return
    global lastSoup, emails, allemails

    email_re = re.compile(r'([\w\.,]+@[\w\.,]+\.\w+)')

    contactFormLink = ""
    try:
        result = r.get(companyUrl.strip(), timeout=to)
    except:
        print("✘  timeout")
        return
    
    soup = bs(result.text.lower(), "html.parser")
    lastSoup = soup
    result.close()

    links = soup.find_all('a')
    
    contactURL = ""
    contactURLs = []

    if len(links)==0:
        return
    
    for link in links:
        href = link.get('href')
        if href == None: href = ""
        
        lrc = link.get('class')
        if lrc != None: linkClass = set(lrc)
        else: linkClass = {}

        for contactWord in contactWords:
            if contactWord in linkClass:
                contactURL = urljoin(companyUrl, href)
                if v: print("Contact URL from link class (%s): %s"%(contactWord, contactURL))
                break

        for contactWord in contactWords:
            if len(link.contents)==0: continue
            if contactWord in link.contents[0]:
                contactURL = urljoin(companyUrl, href)
                if v: print("Contact URL from word (%s): %s"%(contactWord , contactURL))
                break

        for contactWord in contactWords:
            if contactWord in href:
                contactURL = urljoin(companyUrl, href)
                if v: print("Contact URL from href (%s): %s"%(contactWord , contactURL))
                break
        
        if contactURL!="":
            contactURLs.append(contactURL)

    if len(contactURLs) == 0:
        print("  ✘ Contact page")
        return
    else: print("  ✔ Contact page")

    for url in set(contactURLs):
    
        result = r.get(url, headers=headers, params=params, timeout=to)
        soup = bs(result.text.lower(), "html.parser")
        lastSoup = soup
        result.close()
        if soup==None: return

        links = soup.find_all('a')
        email = []

        if len(links)==0:
            return
        
        for link in links:
            href = link.get('href')
            if href == None: href = ""
            
            lrc = link.get('class')
            if lrc != None: linkClass = set(lrc)
            else: linkClass = {}

            if "mailto" in href:
                #print('Found an email link: %s'%href)
                email.append(href.replace("mailto:", ""))

            
        regex_emails = email_re.findall(soup.text)
        for i in regex_emails:
            email.append(i)
        
        if len(email)==0:
            break
    allemails+=email
    if len(email)==0:
        print("  ✘ Email")
    else:
        emails+=[email[0]]
        print("  ✔ Email")
        return email

getAll()
