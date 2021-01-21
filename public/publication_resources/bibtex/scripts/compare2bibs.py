#Author: Leo Lahti
#Date: 17.1.2007
#Comment: works ok.

#Compare citation keys in the my.bbl to those in target.bib
#Add missing keys from my.bib to target.bib.
#Print list of the missing keys and the common keys between my.bbl and target.bbl
#Print missing citations to citationsNotInTargetBib.bib
#Check results manually afterwards and metacontrol produced bibfile

#usage: python compare2bibs.py my.bbl my.bib target.bib

#purpose: copy citations from my bib file to group bib files after the references have been
#selected for the publication and are printed to *.bbl file.

#mybbl="manuDraft.bbl"
#mybib="leo.bib"
#targetbib="gene.bib"

from string import split,strip
import sys

#read bbl file name
mybbl=sys.argv[1]
print(mybbl)
#read my.bib file name
mybib=sys.argv[2]
print(mybib)
#read target.bib file name
targetbib=sys.argv[3]
print(targetbib)

#read bbl file
f=open(mybbl,'r')
bblfields=map(lambda line: strip(line), f.readlines())
f.close()

#read my.bib 
f=open(mybib,'r')
myfields=map(lambda line: strip(line), f.readlines())
f.close()

#read target.bib 
f=open(targetbib,'r')
tfields=map(lambda line: strip(line), f.readlines())
f.close()

#Extract keys in bbl
cnt=0
keys=[]
while cnt<len(bblfields):
    line=bblfields[cnt]
    if "bibitem{" in line:
        key=line[(line.index("{")+1):line.index("}")]
        keys.append(key)
    cnt=cnt+1

#Extract keys in target.bib
cnt=0
tkeys=[]
while cnt<len(tfields):
    line=tfields[cnt]
    if "@Article{" in line:
        key=line[(line.index("{")+1):line.index(",")]
        tkeys.append(key)
    cnt=cnt+1

#search the target.bib for keys in my.bbl
#list keys that are and are not in the target.bib
yeskeys=[]
notkeys=[]
for key in keys:
    if key in tkeys:
        yeskeys.append(key)
    else:
        notkeys.append(key)

print "These keys from",mybbl,"were already included in the", targetbib
print(yeskeys)
print "These keys from",mybbl,"were not included in the", targetbib
print(notkeys)

#Go through keys not in target.bib.
#Get corresponding bib citations from my.bib
#Print these to separate file

f=open("citationsNotInTargetBib.bib",'w')
for key in notkeys:
    #Search this key from my.bib

    cnt=0
    line=myfields[cnt]
    while "{"+key+"," not in line:
        cnt=cnt+1
        line=myfields[cnt]
    keyIndex=cnt
    #read fields for this citation
    citlines=[]
    cnt=keyIndex-1
    cnt=cnt+1
    line=myfields[cnt]
    citlines.append(line)
    f.write(line+"\n")
    while line!='}':
        cnt=cnt+1
        line=myfields[cnt]
        citlines.append(line)
        if line!='}':
            f.write("\t"+line+"\n")
        else:
            f.write(line+"\n")
    f.write("\n\n")

f.close()













