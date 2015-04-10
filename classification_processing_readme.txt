Classification processing README
--------------------------------

Zooniverse offers a huge file for download which includes all 
classifications ever made. Before running these scripts, make sure 
that all tutorial classifications have been removed. Also remove all 
subjects that retired as 'blank' or 'consensus_blank'. For 
efficiency, it is also useful to divide the data up into seasons. 
After that, run these scripts:

1. Clean up the data and make it publishable
--------------------------------------------
prep_season.py <number> <in-file>

This script does some heavy-duty clean up of the file its given. Its 
two main tasks are:
   (1) Condenses classifications that need it. For example, if a user
       specified 2 wildebeest standing and 1 wildebeest moving as
       separate classifications for the same subject, this script
       collapses those two classifications into a single
       classification of 3 wildebeest standing and moving. 
   (2) Anonymizes the user data. It calculates a hash code for each
       user and substitutes this hash in the user column. This allows
       us to share and make public the data without users being
       identifiable. Not-loggged-in users are not anonymized as they
       are already anonymous.
The script takes as input a number representing the season number and 
an input file. It creates TWO output files. The first is called 
'season_<number>.csv' and consists of the cleaned, anonymized data. 
If the script is run with an input file that has already had its 
blanks removed (see above), then this file is the publishable raw 
product for this season, and can be published and shared. The second 
output file is a table of all the user-names and their associated 
hash codes. This table allows us to do look-ups on particular users 
for maintenance reasons. It is not published or shared.


2. Calculate the consensus vote for each subject
------------------------------------------------
plurality_consensus.py <infile> <outfile>

This script performs the plurality algorithm to decide the consensus 
vote for each subject. It takes as input a file that has been cleaned 
(see 1 above) and outputs the consensus vote for each subject -- one 
row per subject and consensus species. Included are measures of 
certainty and other statistics. In particular, it does the following:
   (1) For each subject, blanks are removed (and counted) and the 
       median number of species identified per classification
       (rounded up) is taken as the consensus number of species in 
       the subject/capture.
   (2) For each subject, the species are sorted by the number of
       votes received and the top consensus number of species are
       selected as "winners". If there is a tie, then a species is
       selected randomly from the tied species.
   (3) The count of each winning species is determined as the median 
       number (rounded up) of animals counted for each vote for that 
       species. Minimums and maximums are also reported.
   (4) For each winning species, the percentage of "true" votes is    
       tallied from the votes for that species for'standing', 
       'resting', 'moving', 'eating', 'interacting', and 'babies'.

Metrics for each subject that are recorded are:
   (1) The number of total classifications done
   (2) The number of those that were blanks (i.e. "nothing here")
   (3) The total number of votes cast, which is always greater than
       or equal to the number of classifications minus the number of
       blanks. 
   (4) The Pielou evenness index, which is described here:
       http://en.wikipedia.org/wiki/Species_evenness
       Values range between zero and one, with low numbers having
       more skew and high numbers being more even. The index is 
       calculated on the non-blank votes for each subject. Thus,
       low scores indicate  more certainty about the correctness of
       the classification. In particular, a score of zero indicates
       full consensus. Note that the Pielou evenness index does not
       work well on subjects containing more than one species.
   (5) For each winning species, "species fractional support". This 
       metric describes the number of classifiers who counted this
       species. It is calculated as (number of votes for this   
       species) divided by (number of classifications - number of 
       blanks). For subjects with more than one species, this number 
       gives a much better sense of certainty than the Pielou 
       evenness index. For example, consider a case where there is a 
       zebra and a wildebeest, and each of 9 people identify them 
       correctly, while one person only notes the zebra.The Pielou 
       index would be 0.998, indicating almost complete evenness and 
       wrongly suggesting low certainty. However, the "species 
       fractional support" would be 1.0 for the zebra and 0.9 for the   
       wildebeest, indicating high certainty for both.
   

