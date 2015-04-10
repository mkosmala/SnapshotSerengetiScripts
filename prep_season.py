#!/usr/bin/python

# ------------------------------------------------------------
#
# This script cleans a data dump from the Zooniverse database
# for Snapshot Serengeti. It is expected that subjects that
# retired as 'blank' or 'consensus_blank' and tutorial
# classifications have been removed, and that the the data
# passed in come from a single season. The script creates
# an output file called 'season_<number>.csv' containing the
# cleaned classifications and a file called
# 'season_<number>_hashes.csv' containing anonymized user
# names.
#
# Usage: rep_season.py <number> <infile>
# <number> is the season number
# <infile> is a comma-separated value flat file as dumped
#           from the Zooniverse database.
# 
# Input and output file fields:
#    classification_id
#    user_hash
#    subject_zooniverse_id
#    capture_event_id
#    created_at_time
#    retire_reason
#    season
#    site
#    roll
#    filenames
#    species
#    species_count
#    standing
#    resting
#    moving
#    eating
#    interacting
#    babies
#
# Copyright (C) 2015  Margaret Kosmala (mkosmala@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------

import sys
import csv
import hashlib

# global
hashtable = {}

# Compare two classification lines by species
# Input: two lists (classification lines)
# Outuput: negative if species a < species b, zero if species a ==
#          species b and strictly positive if species a > species b.
def compare_by_species(a,b):
    return cmp(a[11],b[11])

# Conduct logical OR on text values of "true" and "false"
# Input: two values either "true" or "false"
# Ouput: text "true" or "false" representing logical OR of inputs
def combineTF(str1,str2):
    if str1.lower()=="true" or str2.lower()=="true":
        return "true"
    return "false"

# Have we already seen this user? If not, hash it and add to our table.
# Input: user name
# Output: hashed user name
def get_user_hash(username):
    global hashtable
    if username in hashtable:
        thehash = hashtable[username]
    else:
        if username[0:13] == "not-logged-in":
            thehash = username
        else:
            thehash = hashlib.sha224(username[0:39]).hexdigest()
        hashtable[username] = thehash
    return thehash

# For each classification, see if any species is listed more than
# once. If so, combine.
# Input: list of classificiation lines
# Output: cleaned list of classification lines
def process_classification(classlines):

    # sort by species
    classlines.sort(compare_by_species)
    
    # combine if necessary
    newclasslines = list()
    for line in classlines:

        # first line
        if line == classlines[0]:
            lastline = line

        # same species
        elif line[11] == lastline[11]:

            # animal counts
            if lastline[12] == "11-50" or line[12] == "11-50":
                lastline[12] = "11-50"
            elif lastline[12] == "51+" or line[12] == "51+":
                lastline[12] = "51+"
            else:
                num = int(lastline[12]) + int(line[12])
                if num>10:
                    lastline[12] = "11-50"
                else:
                    lastline[12] = str(num)

            # true-false                   
            lastline[13] = combineTF(lastline[13],line[13])
            lastline[14] = combineTF(lastline[14],line[14])
            lastline[15] = combineTF(lastline[15],line[15])
            lastline[16] = combineTF(lastline[16],line[16])
            lastline[17] = combineTF(lastline[17],line[17])
            lastline[18] = combineTF(lastline[18],line[18])

        # different species
        else:
            newclasslines.append(lastline)
            lastline = line
            
    # last line
    newclasslines.append(lastline)

    # get user hash
    userhash = get_user_hash(lastline[1])

    # output lines
    outlines = list()
    for line in newclasslines:
        outlines.append([line[0],userhash] + line[2:10] + line[11:19])

    return outlines


# --- MAIN ---

# get file names from command prompt
if len(sys.argv) < 3 :
    print ("format: prep_season.py <number> <infile>")
    exit(1)

seasonnum = int(sys.argv[1])
infilename = sys.argv[2]

# open input and output files
outfilename = "season_" + str(seasonnum) + ".csv"
hashfilename = "season_" + str(seasonnum) + "_hashes.csv"

infile = open(infilename, 'rb')
filereader = csv.reader(infile, delimiter=',', quotechar='"')

outfile = open(outfilename,'wb')
filewriter = csv.writer(outfile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_ALL)

hashfile = open(hashfilename,'w')
hashwriter = csv.writer(hashfile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_ALL)

# ignore input header line
filereader.next()

# write output header line
filewriter.writerow(["class_id","user_hash","subject_zooniverse_id","capture_event_id","created_at",
                     "retire_reason","season","site","roll","filenames","species","species_count",
                     "standing","resting","moving","eating","interacting","babies"])

# go through each classification line
lastclass = ""
for line in filereader:

    # gather all lines from one classification
    if line[0] == lastclass:
        thisclass.append(line)
        
    # process old classification and start new classification
    else: 
        if lastclass != "":
            goodclass = process_classification(thisclass)
            for gc in goodclass:
                filewriter.writerow(gc)
        
        thisclass = list()
        thisclass.append(line)
        lastclass = line[0]
        
# process the last classification
goodclass = process_classification(thisclass)
for gc in goodclass:
    filewriter.writerow(gc)

# and save the hash table
hashwriter.writerow(["user_name","user_hash"])
for key,value in hashtable.iteritems():
    hashwriter.writerow([key,value])

# close the files
infile.close()
outfile.close()
hashfile.close()
