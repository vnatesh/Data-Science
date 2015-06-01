#!/usr/bin/env python
# -*- coding: utf-8 -*-



# Created by Vikas Natesh 

### I am using the lastFM API in order to crawl the lastFM website for relevant
### data on artists and how they relate to one another in terms of pop culture
### buzzwords called 'tags'. Each artist has a set of tags associated with them
### that users can create when viewing the website. The more users that tag a
### certain artist with a certain tag, the higher the tag count for that (tag,artist)
### pair. Similarity between two artists is a measure of cosine of angle between
### the two 'tag vectors' for that artist.





import numpy as np
import requests
import time

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

    The code below creates a dictionary of  the form -  artist : [list of counts for each tag] - where
    the counts are preordered according to the order of tag names in the
    'tag_list' list. This ensures that our final matrix is consistent with regards
    to variable ordering in rows and columns
    example: tag_data = {artist1:[1,3,0],artist2:[0,0,4]....}
    In this dict, each artist has the same number of tags and I have made the assumption
    that if an artist does not possess a particular tag, the artist's tag count for
    that tag is zero. This was done to simplify the analysis. While it is true that
    some artists have '0' inputed as a tag count for certain tag, I am assuming that
    this situation is the same as if the artist did not possess that tag at all.
    We may hypothesize that an artist gets a tag count of zero in the case that a
    user/admin tags, but then de-tags the artist for a certain tag. The initial tagging
    would've created a variable for the tag and removing it may have simply caused its
    iteration count to exceed (instead of deleting the tag var as a whole). 


'''

tag_data={x :[] for x in names}
tag_list=list(tag_set)

for name in names:
    for item in tag_list:
        if item in artistTag_dict[name].keys():
            tag_data[name].append(int(artistTag_dict[name][item]))
        else: tag_data[name].append(0)   # assumes absence of a tag is a count of zero


'''

    There are no zero length vectors since we already took care of that step
    when we made the requirement that the 'tag' attribute must be present in the
    JSON for each artist. 

'''

'''

    Now that we have a list of ordered tag counts for each of our artists, we can
    employ a cosine similarity algorithm to the dataset. In this method, we assume
    that the list of tag counts for a particular artist is a vector whose similarity
    to another vector for different artist is simply the cosine of the angle between
    the two vectors. This can be acheived by taking the dot product of the two vectors
    and dividing this by the product of the two vectors' lengths:
    cosine(artist1,artist2) = (artist1_tagCounts) dot (artist2_tagCounts) / (|artist1_tagCounts| * |artist1_tagCounts|)

    This process can then be repeated for all artist pairs, creating a square n X n similarity matrix
    where n is the number of artists. The diagonal values will be all be 1 and the
    matrix is symmetric. All values will be non-negative since there are no negative tag counts.

    In this example, two artists are considered 'similar' if the cosine of the angle between their
    vectors is close to one i.e. two artists are considered similar if they have similar
    tags and tag counts associated with them. Thus it gives us a comparison metric
    for how culturally similar two artists are based on the identities and
    frequencies of all pop culture tags.

'''

''''

    Below, we write our cosine matrix to a new file 'final_data'. It contains artist names
    ordered along row and column headings in the same consistent order. The matrix
    values contain cosines of the angles between the (row-artist,column-artist)
    vector pairs.

'''


with open('%sartist_data.txt' % path,'w') as final_data:
    header='Artist_Name'+'\t'+'\t'.join([y for y in tag_data.keys()])+'\n'
    final_data.write(header.encode("utf-8"))

    for p in tag_data.keys():
        list1=[]
        for q in tag_data.keys():
            list1.append((np.inner(tag_data[p],tag_data[q])) / (np.linalg.norm(tag_data[p])*np.linalg.norm(tag_data[q])))   # cosine step
        row=p+'\t'+'\t'.join(map(str,list1))+'\n'
        final_data.write(row.encode("utf-8"))                                      



final_data.close()

print 'Time Taken : ',time.time()-start,' seconds'





'''

As a different measure of similarity, we could have used correlation by carrying
out the cosine computation using mean-centered versions of the two vectors.The reason
correlation was not used was due to the fact that most cells in the tag matrix
were null entries (0) and not meaningful with regards to the statistical certainty.
It would be interesting to compare artist similarlity based on other api methods
such as 'getTopTracks'and 'getHypedArtists'. We could also use the various 'Geo' methods
to analyze artist similarity based on geographic location. 


'''
