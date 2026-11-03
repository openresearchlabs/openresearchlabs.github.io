#Convert .ris citation file to bibtex format / Leo 6.9.2005

from string import split,strip
import sys

#Read ris file

filename=sys.argv[1]
print(filename)

filenameStart=filename[:-4]

f=open(filename,'r')
fields=map(lambda line: strip(line), f.readlines())
f.close()

#List of supported fields in this script, defaulting empty
authors=''
number=''
title=''
journal=''
volume=''
number=''
startpage=''
endpage=''
url=''
year=''

#init tex fields
authors=[]

#pick essential info
for line in fields:
    if line[0:6]=="AU  - " or line[0:6]=="A1  - ":
        authors.append(line[6:])
    if line[0:4]=="AU: ":
        authors.append(line[4:])        
    if line[0:6]=="TI  - " or line[0:6]=="T1  - ":
        title=line[6:]
    if line[0:4]=="TI: ":
        title=line[4:]        
    if line[0:6]=="JA  - " or line[0:6]=="JO  - ":
        journal=line[6:]
    if line[0:4]=="SO: ":
        journal=line[4:]        
    if line[0:6]=="JF  - ": #prefer longer version of journal name
        journal=line[6:]    
    if line[0:6]=="VL  - ":
        volume=line[6:]
    if line[0:4]=="VL: ":
        volume=line[4:]
    if line[0:4]=="NO: ":
        number=line[4:]
    if line[0:6]=="IS  - ":
        number=line[6:]                        
    if line[0:6]=="SP  - ":
        startpage=line[6:]
    if line[0:4]=="PG: ":
        startpage=split(line[4:],'-')[0]
        endpage=split(line[4:],'-')[1]
    if line[0:5]=="EP  -":
        if line!="EP  -":
            endpage=line[6:]
        else:
            endpage=""
    if line[0:6]=="UR  - ":
        url=line[6:]
    if line[0:4]=="US: ":
        url=line[4:]        
    if line[0:6]=="PY  - " or line[0:6]=="Y1  - ": 
        year=line[6:10]
    if line[0:4]=="YR: ":
        year=line[4:8]

#create reference key
authorsString=""
if authors:
    #form key
    key=split(authors[0],",")[0]+year[2:4]
    #write authors list
    for author in authors[:-1]:
        authorsString=authorsString+author+" and "
    authorsString=authorsString+authors[-1]
else:
    key=""
    

#Check that reference key is not in use already

keyfile="leo.bib"
print(keyfile)

f2=open(keyfile,'r')
keyfields=map(lambda line: strip(line), f2.readlines())
f2.close()

keys=[]
for line in keyfields:
    if line!="":
        if line[0]=="@":
            keys.append(split(line[0:len(line)-1],"{")[1])


if key in keys:
    print("Reference key already in use in leo.bib. Modify reference key.")
    key=key+"b"
    
if key not in keys:
    print("Reference key is ok.")



#write bibtex template
f=open(filenameStart+".bibTemplate",'w')
f.write("@Article{"+key+","+"\n")
f.write("author = {"+authorsString+"},"+"\n")
f.write("title = {"+title+"},"+"\n")
f.write("journal = {"+journal+"},"+"\n")
f.write("year = {"+year+"},"+"\n")
f.write("volume = {"+volume+"},"+"\n")
if number:
    f.write("number = {"+number+"},"+"\n")
if (startpage and endpage):
    f.write("pages = {"+startpage+"--"+endpage+"},"+"\n")
f.write("url = {"+url+"},"+"\n")
f.write("annote = {}"+"\n")
f.write("}\n\n")
f.close()

print("Template done.")





