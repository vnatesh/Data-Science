#*****************   DATA ENGINEER ASSIGNMENT ***************
# Created by Vikas Natesh 




#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import requests
import time
np.seterr(divide='ignore', invalid='ignore')


start=time.time()


# declare a path for the output files

path='/Users/vikasnatesh/Documents/Python/Python_Scripts/'

# destination url for last_fm api

lastFM_url = 'http://ws.audioscrobbler.com/2.0'

# params for the 'get' method for top artists

parameters={'api_key':'c28d8d76684ab88319632875712289dd','format':'json' \
                      ,'method':'chart.getTopArtists','limit':100}

master=requests.get(lastFM_url,params=parameters).json()

data=master['artists']['artist']

'''

    The code below allows us to display relevant data for each artists i.e.
    playcount, listeners, mbid, and corresponding artist name.
    The text file is called 'artist_data.txt'. Artists in the file are ordered
    according to the number of listeners. I also create a list of artist names for convenience.

'''

names=[]


with open('%sartist_IDs.txt' % path,'w') as artist_ids:
    artist_ids.write('Artist Name'+'\t'+'Num_Listeners'+'\t'+'Play_Count'+'\t'+'mbid'+'\n')

    for i in data:
        names.append(i['name'])
        a=i['name']+'\t'+i['listeners']+'\t'+i['playcount']+'\t'+i['mbid']+'\n'
        artist_ids.write(a.encode("utf-8"))

artist_ids.close()


'''

 Now we get each tag/tag_count pair for each artist and construct a dictionary
 'artistTag_dict' of the form - {artist1:{tag1:2,tag2:0..),artist2:(tag1:0,tag2:5}}

'''

# params for the 'get' method for top tags

parameters={'api_key':'c28d8d76684ab88319632875712289dd','format':'json' \
                      ,'method':'artist.getTopTags','limit':100}
    

tag_set=set()
artistTag_dict={}

for artist in names:
    parameters['artist']=artist
    tags=requests.get(lastFM_url,params=parameters).json()
    tag_dict={}
    if 'tag' in tags['toptags']:
        try:
            for tag in tags['toptags']['tag']:
                tag_set=tag_set | set([tag['name']])
                tag_dict[tag['name']]=tag['count']
        except TypeError:
            tag_set=tag_set | set([tags['toptags']['tag']['name']])
            tag_dict[tags['toptags']['tag']['name']]=tags['toptags']['tag']['count']
            
        artistTag_dict[artist]=tag_dict


'''

    The code below creates a dictionary of  the form -  tag : [list of counts for each artist] - where
    the counts are preordered according to the order of artist names in the
    'names' list. This ensures that our final matrix is consistent with regards
    to variable ordering in rows and columns
    example: tag_data = {tag1:[1,3,0],tag2:[0,0,4]....}
    In this dict, each tag has the same number of artists and I have made the assumption
    that if a tag is not associated with a particular artist, the tag's artist count for
    that artist is zero. This was done to simplify the analysis. While it is true that
    some artists have '0' inputed as a tag count for certain tag, I am assuming that
    this situation is the same as if the artist did not possess that tag at all.
    We may hypothesize that an artist gets a tag count of zero in the case that a
    user/admin tags, but then de-tags the artist for a certain tag. The initial tagging
    would've created a variable for the tag and removing it may have simply caused its
    iteration count to exceed (instead of deleting the tag var as a whole). 

'''


tag_list=list(tag_set)           
tag_data={x :[] for x in tag_list}

for item in tag_list:
    for name in names:
        if item in artistTag_dict[name]:
            tag_data[item].append(int(artistTag_dict[name][item]))           
        else: tag_data[item].append(0)

'''

    I remove vectors which have length 0 so as to avoid a 'divide by zero' error
    when we compute the cosine similarity

'''

for n in tag_list:
    if sum(tag_data[n])==0:
        del tag_data[n]



'''

    Now that we have a list of ordered artist counts for each of our tags, we can
    employ a cosine similarity algorithm to the dataset. In this method, we assume
    that the list of artist counts for a particular tag is a vector whose similarity
    to another vector for different tag is simply the cosine of the angle between
    the two vectors. This can be acheived by taking the dot product of the two vectors
    and dividing this by the product of the two vectors' lengths:
    cosine(tag1,tag2) = (tag1_artistCounts) dot (tag2_artistCounts) / (|tag1_artistCounts| * |tag2_artistCounts|)

    This process can then be repeated for all tag pairs, creating a square n X n similarity matrix
    where n is the number of tags. The diagonal values will be all be 1 and the
    matrix is symmetric. All values will be non-negative since there are no negative artist counts.

    In this example, two artists are considered 'similar' if the cosine of the angle between their
    vectors is close to one i.e. two artists are considered similar if they have similar
    tags and tag counts associated with them. Thus it gives us a comparison metric
    for how culturally similar two tags are, based on the identities of their respective associated 
    artists as well as how frequently this association takes place for each artist.

'''

'''

    Below, we write our cosine matrix to a new file 'final_data'. It contains artist names
    ordered along row and column headings in the same consistent order. The matrix
    values contain cosines of the angles between the (row-artist,column-artist)
    vector pairs.

'''

with open('%stag_data.txt' % path,'w') as final_data:
    header='Tag_Name'+'\t'+'\t'.join([y for y in tag_data.keys()])+'\n'
    final_data.write(header.encode("utf-8"))

    for p in tag_data.keys():
        list1=[]
        for q in tag_data.keys():
            list1.append((np.inner(tag_data[p],tag_data[q])) / (np.linalg.norm(tag_data[p])*np.linalg.norm(tag_data[q])))   # cosine step
        row=p+'\t'+'\t'.join(map(str,list1))+'\n'
        final_data.write(row.encode("utf-8"))                                      



final_data.close()

print 'Time Taken : ',time.time()-start,' seconds'





