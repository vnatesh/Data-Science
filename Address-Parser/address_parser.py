import sys,re, string


print 'Address Representations'+'\n'



class Address:

    def set_company(self,inp):
        self.company=inp
        
    def set_zip_code(self,inp):
        self.zip_code=inp
        
    def set_building_num(self,inp):
        self.building_num=inp
        
    def set_city(self,inp):
        self.city=inp

    def set_state(self,inp):
        self.state=inp

    def set_street_name(self,inp):
        self.street_name=inp

    def set_street_type(self,inp):
        self.street_type=inp

    def set_street_dir(self,inp):
        self.street_dir=inp

    def set_building_unit(self,inp):
        self.building_unit=inp

    def get_key(self):
        return (self.building_num,self.street_name,self.street_type,self.zip_code)

    def __str__(self):
        return (str(self.building_num) + ' ' + str(self.street_dir)+' '+
    str(self.street_name) + ' ' + str(self.street_type) 
    + ' ' + str(self.city) + ' ' + str(self.state) + ' ' + str(self.zip_code))
        


street_types={'Ave':'Avenue','Ave.':'Avenue','Blvd':'Boulevard','Blvd.':'Boulevard','St':'Street','St.':'Street'}
dirs=['N','N.','S','S.','E','E.','W','W.','NE','SE','NW','SW']

#addresses = open(sys.argv[1],'r')


master=[]
addresses=open('/Users/vikasnatesh/Downloads/data_analyst_exercise/Data/addresses.csv','r')

for case in addresses.read().split('\r')[1:]:
    
    case = re.findall(r'\w+',case)
    for p in xrange(len(case)):
        if case[p] in street_types.keys():
            case[p]=street_types[case[p]]
            
    case[1]=int(case[1])   # convert building number to an int to avoid indexing confusion
                           # in case the street name is the same number as building number

    company=case[0]
    i=case[1:]


    address = Address()
    address.set_company(company)
    address.set_zip_code(i[-1])
    address.set_building_num(i[0])
    address.set_city(i[-3])
    address.set_state(i[-2])


    street = i[1:-3]
    
    
    list1=[]

    j=0
    while j<len(street):
        if street[j] in street_types.values():
            address.set_street_type(street[j])
            j+=1
        elif street[j] in dirs:
            address.set_street_dir(street[j])
            j+=1
        else:
            list1.append(street[j])
            j+=1


    try: a=address.street_type
    except AttributeError: address.set_street_type(None)

    try: a=address.street_dir
    except AttributeError: address.set_street_dir(None)

    s=''
    
    for k in list1:
        if i.index(address.building_num)<i.index(k)<i.index(address.street_type):
            if k in string.digits:
                address.set_street_name(k)
            elif k[0] in string.digits:
                address.set_street_name(k[:-2])
            else: address.set_street_name(k)
        else: s+=k

    try: a=address.street_name
    except AttributeError: address.set_street_name(None)

    if s!='':
        address.set_building_unit(s)
    else: address.set_building_unit(None)
        
    print address
    master.append(address.get_key())

print '\n\n'
print "Unique Address List"+'\n'
for item in set(master):
    print item


