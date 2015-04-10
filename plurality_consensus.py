#!/usr/bin/python

# ------------------------------------------------------------
#
# This script calculates the "plurality" consensus of species
# classifications for Snapshot Serengeti images. Plurality
# simply means the species that garners the most votes
# regardless of whether or not that species gets at least half
# of all votes ("majority").
#
# Usage: plurality_consensus.py <infile> <outfile>
# <infile>  is a comma-separated value flat file as dumped
#           from the Zooniverse database.
# <outfile> is the file to be written to (.csv format) In this
#           file, each line represents a consensus species
#           within a subject. Subjects with just one species
#           will contain one line in this file. Subjects with
#           two species will contain two lines. Etc.
#
# Input file fields:
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
# Output file fields:
#    subject_zooniverse_id
#    capture_event_id
#    retire_reason
#    season
#    site
#    roll
#    filenames
#    number_of_classifications
#    number_of_votes
#    number_of_blanks
#    pielou_evenness
#    number_of_species
#    species_index
#    species
#    species_votes
#    species_fraction_support
#    species_count_min
#    species_count_median
#    species_count_max
#    species_fraction_standing
#    species_fraction_resting
#    species_fraction_moving
#    species_fraction_eating
#    species_fraction_interacting
#    species_fraction_babies
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
import math
import random
import operator

# Compare two lists by comparing their first item
# Input: two lists (lines from the input file)
# Output: negative if a[0] < b[0], zero if a[0] == b[0] and
#         strictly positive if a[0] > b[0].
def compare_by_classification(a,b):
    return cmp(a[0],b[0])

# Return the number of species in classifications for a given subject.
# Input: a list of classifications, wherein each classification is a list
#        of species (with associated data)
# Output: a list with the number of species per classification
def get_species_counts(scals):
    spp = list()
    for cl in scals:
        if cl[0][10] != "": # ignore blanks
            spp.append(len(cl))
        else:
            spp.append(0)
    return spp

# Returns a dictionary giving the vote tallies for a subject
# Input: a list of classifications lines, each of which is a list
# Output: a dictionary with species as the key and the number of votes
#         the species received as value
def tally_spp_votes(subject):
    vote_table = {}
    for entry in subject:
        spp = entry[10]
        if spp != "": # ignore blanks
            # already in table
            if spp in vote_table:
                vote_table[spp] = vote_table[spp] + 1
            # not in table yet
            else:
                vote_table[spp] = 1
    return vote_table

# Calculate the Pielou Evenness Index
# Input: a list giving the distribution of votes
# Output: the Pielou Evenness Index or 0 for unanimous vote
def calculate_pielou(nlist):
    if len(nlist)<2:
        return 0 
    # denominator
    lnS = math.log(len(nlist))
    # numerator
    sumlist = sum(nlist)
    plist = [float(n)/sumlist for n in nlist]
    plnplist = [n * math.log(n) for n in plist]
    sumplnp = -sum(plnplist)
    return sumplnp/lnS    

# Choose the winners from the vote as the top vote-getters.
# Input: number of winners
# Input: a dictionary of votes
# Output: a list of the winning species
def choose_winners(numwin,sppvotes):
    # sort by votes
    sorted_sppvotes = sorted(sppvotes.iteritems(),
                             key=operator.itemgetter(1),
                             reverse=True)
    winners = sorted_sppvotes[0:numwin]

    # check for ties
    if len(sorted_sppvotes) > numwin:
        if sorted_sppvotes[numwin-1][1] == sorted_sppvotes[numwin][1]:
            votes = sorted_sppvotes[numwin-1][1]
            ties = []
            # get all the tied species
            for spp in sorted_sppvotes:
                if spp[1] == votes:
                    ties.append(spp)
            # choose one at random
            tiewinner = random.choice(ties)
            winners[numwin-1] = tiewinner

    return winners

# Calculate the number of individuals within a species based on
# bins (1,2,3,4,5,6,7,8,9,10,11-50,51+)
# Input: a list of the number of individuals given for a species
# Output: a list giving the minimum, median, and maximum bin
def calculate_num_animals(noa):
    
    nums = []
    tens = []
    meds = []
    many = []
    for ea in noa:
        if len(ea)==1:
            nums.append(ea)
        elif ea=="10":
            tens.append(ea)
        elif ea=="11-50":
            meds.append(ea)
        else:
            many.append(ea)
    nums.sort()
    sorted_list = nums + tens + meds + many
    # round up (gotta choose one or the other)
    medind = int(math.ceil((len(sorted_list)+1)/2)-1)
    return [sorted_list[0],sorted_list[medind],sorted_list[-1]]

# Calculate the percentage of true items given a list of true and false
# Input: a list of true and false items
# Output: the fraction of true items in the list expressed as a decimal
def calculate_TF_perc(items):
    ctr = 0
    for ea in items:
        if ea=="true":
           ctr = ctr + 1
    return float(ctr) / len(items)

# Return metadata associated with the winning species
# Input: a list of species winners, each of which is a list
# Input: total number of classifications
# Input: total number of blanks
# Input: a list of classification lines, each of which is a list
# Output: a list containing statistics for each species provided
def winner_info(sppwinners,numclass,numblanks,subject):
    info = []
    for spp in sppwinners:
        # fraction people who voted for this spp
        fracpeople = float(spp[1]) / (numclass-numblanks)
        # look through votes
        noa = []
        stand = []
        rest = []
        move = []
        eat = []
        interact = []
        baby = []

        for line in subject:
            if line[10]==spp[0]:
                noa.append(line[11])
                stand.append(line[12])
                rest.append(line[13])
                move.append(line[14])
                eat.append(line[15])
                interact.append(line[16])
                baby.append(line[17])
        
        # number of animals
        numanimals = calculate_num_animals(noa)
        
        # true-false questions
        stand_frac = calculate_TF_perc(stand)
        rest_frac = calculate_TF_perc(rest)
        move_frac = calculate_TF_perc(move)
        eat_frac = calculate_TF_perc(eat)
        interact_frac = calculate_TF_perc(interact)
        baby_frac = calculate_TF_perc(baby)
        
        # save it all
        info.append([spp[0],spp[1],fracpeople] + numanimals +
                    [stand_frac,rest_frac,move_frac,eat_frac,
                     interact_frac,baby_frac])
        
    return info

    
# Process all the classifications for one subject and write the
# plurality consensus vote for that subject to the output file.
# Input: a list that contains classification lines from the flat file.
#        Each classification line is itself a list, with each item in
#        the list a datum from the input flat file.
# Output: none
def process_subject(subject,filewriter):
    
    # sort by classification so that multiple lines within
    # one classification are adjacent
    subject.sort(compare_by_classification)

    # create a 2D list: first by classification, then by species
    scals = list()
    lastclas = ""
    subcl = list()
    for entry in subject:
        if entry[0] == lastclas:
            subcl.append(entry)
        else:
            if len(subcl)>0:
                scals.append(subcl)
            subcl = [entry]
            lastclas = entry[0]
    scals.append(subcl)

    # count total number of classifications done
    numclass = len(scals)

    # count unique species per classification, ignoring blanks
    sppcount = get_species_counts(scals)

    # count and remove the blanks
    numblanks = sppcount.count(0)
    sppcount_noblanks = list(value for value in sppcount if value != 0)

    # take median (rounded up) of the number of individuals in the subject
    sppcount_noblanks.sort()
    medianspp = sppcount_noblanks[int(math.ceil((len(sppcount_noblanks)+1)/2)-1)]

    # count up votes for each species
    sppvotes = tally_spp_votes(subject)

    # total number of (non-blank) votes
    totalvotes = sum(sppvotes.values())

    # Pielou evenness index
    pielou = calculate_pielou(sppvotes.values())

    # choose winners based on most votes
    sppwinners = choose_winners(medianspp,sppvotes)

    # get winner info
    winnerstats = winner_info(sppwinners,numclass,numblanks,subject)

    # output to file
    basic_info = (subject[0][2:4] + subject[0][5:10] +
                  [numclass,totalvotes,numblanks,pielou,medianspp])
    ctr = 1
    for winner in winnerstats:
        spp_info = basic_info + [ctr] + winner
        filewriter.writerow(spp_info)
        ctr = ctr + 1

    return


# --- MAIN ---

# get file names from command prompt
if len(sys.argv) < 3 :
    print ("format: plurality_consensus.py <infile> <outfile>")
    exit(1)

# open the infput and output files
infilename = sys.argv[1]
outfilename = sys.argv[2]

infile = open(infilename, 'rb')
filereader = csv.reader(infile, delimiter=',', quotechar='"')

outfile = open(outfilename,'wb')
filewriter = csv.writer(outfile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_NONE)

# ingore the header line in the input file
filereader.next()

# write the header line for the output file
filewriter.writerow(["subject_zooniverse_id","capture_event_id","retire_reason",
                     "season","site","roll","filenames",
                     "number_of_classifications","number_of_votes",
                     "number_of_blanks","pielou_evenness",
                     "number_of_species","species_index",
                     "species","species_votes","species_fraction_support",
                     "species_count_min","species_count_median","species_count_max",
                     "species_fraction_standing","species_fraction_resting",
                     "species_fraction_moving","species_fraction_eating",
                     "species_fraction_interacting","species_fraction_babies"])


# sort the classifications by subject
sortedclass = sorted(filereader, key=operator.itemgetter(2))

# go through the subjects one by one
lastsubject = sortedclass[0][2]
subjectlines = []
for entry in sortedclass:
    subject = entry[2]

    # gather all the classification for each subject
    if subject == lastsubject:
        subjectlines.append(entry)
        
    else:
        # process all the classifications for one subject
        process_subject(subjectlines,filewriter)
        subjectlines = [entry]
        lastsubject = subject

# process the last subject
process_subject(subjectlines,filewriter)
        
# close the input and output files        
infile.close()
outfile.close()
