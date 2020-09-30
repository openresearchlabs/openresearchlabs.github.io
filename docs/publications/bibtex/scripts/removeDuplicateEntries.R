#
# Remove identical duplicate entries in bib file
#

# Define in and output file
infile = "leo.bib"
outfile = "leo.bib.new"
con = file(description = outfile, open = "w")


# Read file
lins = readLines(infile)

# List line indices for bib entries
entrylineinds = grep("@",lins)
entrylineinds = entrylineinds[grep("\\{",lins[entrylineinds])]
entrylineinds = entrylineinds[grep("\\,",lins[entrylineinds])]

keylines = lins[entrylineinds]

# List unique entry keys
keys = unlist(lapply(keylines,function(x){unlist(strsplit(x,"\\{"))[[2]]}))
keys.uniq = unique(keys)

# For each unique key, find the corresponding entries
warns = c()
duplicated.kept = c()
for (unikey in keys.uniq) {
	print(unikey)
	# Get keyline indices for this key
	inds = entrylineinds[grep(unikey,keylines)]	
	endinds = c()
	entrydata = list()
	cnt = 0
	for (ind in inds) {
		# Find the last line of this entry
		# i.e. the next entry minus one
		latterlines = which(entrylineinds > ind)
		if (length(latterlines)>0) {
			cnt = cnt + 1
			endind = entrylineinds[which(entrylineinds > ind)[[1]]]- 1
			endinds[[cnt]] = endind
			entrydata[[cnt]] = lins[ind:endind]
		} else {break}		
	}
	# Remove emtpy lines from each entry
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x==""}))]})
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x==" "}))]})
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x=="  "}))]})
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x=="   "}))]})
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x=="    "}))]})
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x=="     "}))]})
	entrydata = lapply(entrydata,function(x){x[unlist(lapply(x,function(x){!x=="\t"}))]})
	# Compare listed items and list those that are not identical
	unique.entries = list(entrydata[[1]])
	cnt = 1
	if (length(entrydata)>1) {
		for (i in 2:length(entrydata)) {
			if (!length(entrydata[[i]]) == length(entrydata[[1]])) {warns = c(warns,unikey)}
			if (!all(entrydata[[1]] == entrydata[[i]])) {
				# If everything not identical, save both
				cnt = cnt + 1
				unique.entries[[cnt]] = entrydata[[i]]
			}
		}
	}

	if (length(unique.entries)>1) {duplicated.kept = c(duplicated.kept,unikey)}

	# Write the unique entries
	for (item in unique.entries) {
		writeLines(unlist(unlist(item)),con)

	}	
	writeLines("\n",con)
}

close(con)

print("Remember to check warns and duplicated.kept manually.")
