#Convert .bib citation to summary format / Leo 12.4.2005

#Currently ok for articles. Needs some modifications to write also
#books, TechReps etc nicely,

from string import split,strip
import sys

#Read citation key

citkey=sys.argv[1]
print(citkey)

#read bib file

f=open('leo.bib','r')
fields=map(lambda line: strip(line), f.readlines())
f.close()

#search the article for the key
cnt=0
line=fields[cnt]
while "{"+citkey not in line:
    cnt=cnt+1
    line=fields[cnt]

keyIndex=cnt

#initialize 
author=''
title=''
publication=''
volume=''
number=''
pages=''
year=''
url=''
annote=''


#read fields

while line!='}':
    cnt=cnt+1
    line=fields[cnt]
    if line[0:6].lower()=='author':
        eind=line.index("{")+1
        if "}" in line:
            cind=line.index("}")
            author=line[eind:cind]
        else:
            cind=len(line)
            author=split(line[eind:cind],",")[0]+" et al."
    if line[0:5].lower()=='title':
        if line.count("{")==1:
           bracketStart=line.index("{")
        if line.count("{")==2:
           bracketStart=line.index("{")+1
        if "}" in line:
            title=line[bracketStart+1:line.index("}")]
        else:
            title=line[line.index("{")+1:]
            while "}" not in line:
                cnt=cnt+1
                line=fields[cnt]
                splitline=split(strip(line),"}")[0]
                title=title+" "+splitline
    if line[0:7].lower()=='journal':
        publication=line[line.index("{")+1:line.index("}")]
    if line[0:6].lower()=='volume':
        eind=line.index("\t")
        cind=line.index(",")
        volume=strip(line[eind:cind])
    if line[0:6].lower()=='number':
        eind=line.index("\t")
        cind=line.index(",")
        number=strip(line[eind:cind])
    if line[0:5].lower()=='pages':
        pages=line[line.index("{")+1:line.index("}")]
    if line[0:4].lower()=='year':
        eind=line.index("\t")
        cind=line.index(",")
        year=strip(line[eind:cind])
    if line[0:3].lower()=='url' or line[0:3]=='URL':
        if "{" in line:
            url=line[line.index("{")+1:line.index("}")]
        else: #long row has actually been placed to next row..
            tmpline=fields[cnt+1] 
            url=tmpline[tmpline.index("{")+1:tmpline.index("}")]
    if line[0:6].lower()=='annote':        
        if "}" in line:
            annote=line[line.index("{")+1:line.index("}")]
        else:
            annote=line[line.index("{")+1:]
            while "}" not in line:
                cnt=cnt+1
                line=fields[cnt]
                splitline=split(strip(line),"}")[0]
                annote=annote+" "+splitline


    
#write to file


f=open(citkey+".tmp",'w')
f.write(author+" ("+year+")\n")
f.write(title+". \n")
f.write(publication+" ")
if volume:
    f.write(volume)
if number:
    f.write("("+number+")")
if pages:
    f.write(" pp. "+ pages)
f.write(", "+year+".\n")
if url:
    f.write(url)
if annote:
    f.write("\n"+annote)
f.close()








