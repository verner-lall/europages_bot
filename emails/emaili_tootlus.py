from validate_email import validate_email
from os.path import isfile

tick = "✔ "
cross = "✘ "
pause_on_no = False
hide_info = True
hide_false = False
hide_valid = True

error = {}
check = {}
good = {}

def add(email, to):
    if email.domain in to:
        to[email.domain].append(email)
    else:
        to[email.domain] = [email]

def show(to):
    for domain in to:
        print(domain)
        for email in to[domain]:
            print("  "+str(email))

def select_from(to):
    emails = []
    for domain in to:
        emails.append(select(to[domain]))
    return emails

def info(text):
    if not hide_info:
        print(text)
def y(text, space=0):
    if not hide_valid:
        info(" "*space+tick+text)
def n(text, space=0, ipt=""):
    if hide_false:
        return
    info(" "*space+cross+text)
    if pause_on_no:
        return input(ipt)

def select(email_list):
    if len(email_list)==0: return None
    if len(email_list)==1:
        return email_list[0]
    for email in email_list:
        e = email.email
        if "contact" in e: return email
        if "info" in e: return email
    return email_list[0]

def get_page(page):
    fn = "page%s.txt"%str(page)
    emails = []
    file = open(fn, encoding='utf8')
    for line in file:
        emails.append(line.strip().split(" "))
    file.close()
    return emails

def process_page(emails):
    for raw_email in emails:
        if len(raw_email)==2:
            domain = raw_email[1]
        else:
            domain = None    
        email = process(raw_email[0], domain)

        if email.valid:
            add(email, good)
        else:
            if email.dot == "":
                add(email, error)
            else:
                add(email, check)
        

class Email(object):
    def __init__(self, e, d, v, dot):
        self.email = e
        self.domain = d
        self.valid = v
        self.dot = dot
    def __str__(self):
        string = ""
        if self.valid:
            string+=tick
        else:
            string+=cross
        return string + " %s"%self.email

invalid = "!'#¤%&/()=£$€{[]}\+´`~Ž><|:;*öäõüÄÖÕÜðÐþÞ"+'"'

def process(email, domain = None):
    info(email)
    if "?" in email:
        email = email.split("?")[0]
    if "%20" in email:
        email = email.replace("%20","")
    valid = validate(email)
    for i in invalid:
        if i in email:
            valid = False
    if not valid: return Email(email, "", False, "")
    
    dot = dot_what(email)
    
    if domain == None:
        domain = email.split("@")[1]

    if not dot[0]:
        return Email(email, domain, False, dot[1])

    info("Domain: %s"%str(domain))
    return Email(email, domain, True, dot[1])
    


def dot_what(email):
    s = email.split(".")
    end = s[-1]
    if len(end)>4 or len(end)<=1:
        n(".end : %s"%(end))
        return (False, end)
    else:
        y(".end")
        return (True, end)
    

def validate(email):
    valid = validate_email(email)
    if valid:
        y("Valid")
        return True
    else:
        n("Valid")
        return False

def do(start=1, end=180):
    for page_nr in range(start,end):
        page = get_page(page_nr)
        process_page(page)
    ship = select_from(good)
    return ship

def save(a, fn):
    file = open(fn, 'w', encoding='utf8')
    x = len(a)/10
    i = 0
    print("#"*10)
    for email in a:
        i+=1
        if i%x==0:
            print("#",end='')
        file.write(email.email+"\n")
    file.close()
    print("\nFile saved to " + fn)
