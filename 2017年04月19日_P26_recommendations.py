

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt
# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs,p1,p2):
    # Get the list of mutually rated items
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1

    # Find the number of elements
    n=len(si)

    # if they are no ratings in common, return 0
    if n==0: return 0

    # Add up all the preferences
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])

    # Sum up the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])

    # Sum up the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])

    # Calculate Person score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0

    r=num/den

    return r

# Returns the best matches for person from the prefs dictionary
# Numbers of results and similarity function are optional params
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores=[(similarity(prefs,person,others),others)
                    for others in prefs if others!=person]
# Sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]

print(topMatches(critics,'Toby',n=3))


# Get recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        if other==person: continue
        sim=similarity(prefs,person,other)

        # ignore scores of zero or lower
        if sim<=0: continue
        for item in prefs[other]:

            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
                # Similarity * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim   #代码竟然抄错，显然理解不够深刻
                # sum of similarity
                simSums.setdefault(item,0)
                simSums[item]+=sim

    # Create the normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
                                            #顺序竟然不能颠倒
    # Return the sort list
    rankings.sort()
    rankings.reverse()
    return rankings

def transformprefs(prdfs):
    results={}
    for person in prdfs:
        for item in prdfs[person]:
            results.setdefault(item,{})

            # Flip item and person
            results[item][person]=prdfs[person][item]
    return results

movies=transformprefs(critics)
print(topMatches(movies,'Superman Returns'))
print(getRecommendations(movies,'Just My Luck'))

def calculateSimilarItems(prdfs,n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to
    result={}

    # Invert the preference matrix to be item-centric
    itemPrefs=transformprefs(prdfs)
    c=0
    for item in itemPrefs:
        # Status updates for large datasets
        c+=1
        if c%100==0:
            print ("%d / %d " % (c,len(itemPrefs)))
        # Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_pearson)
        result[item]=scores
    return result

itemsim=calculateSimilarItems(critics)

def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}

    # Loop over items rated by this user
    for (item,rating) in userRatings.items():

        # Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings: continue

            # Weight sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating

            # sum of all the similarity
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity

    # Divide each total score by total weighting to get an average
    rankings=[(score/totalSim[item]) for item,score in scores.items()]

    # Retrun the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

def loadMovieLens(path='./ml-latest-small'):

    # Get movie titles
    movies={}
    for line in open(path+'/movies.csv'):
        (id,title)=line.split(',')[0:2]
        movies[id]=title

    # Load data
    prefs={}
    for line in open(path+'/ratings.csv'):
        (user,movieid,rating,ts)=line.split(',')
        prefs.setdefault(user,{})
        try:
            prefs[user][movies[movieid]]=float(rating)
        except ValueError as e:
            print('error',e)


    return prefs

prefs=loadMovieLens()
print('************************************')
print(prefs['87'])

print(getRecommendations(prefs,'87')[0:30])

print('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
itemsim=calculateSimilarItems(prefs,n=50)
print(itemsim)
