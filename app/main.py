from flask import Flask, redirect, request, render_template
import requests
import json
import random
import dateutil.parser
import datetime
#CODE WRITTEN BY JAMES ROWLAND
#API TOKEN CHANGED BECAUSE GITHUB SECURITY CANCELS MY TOKEN IF I UPLOAD IT
api_token = '8c339686419cf727c52b263b027c42fd13XXXXXX'
token_AuthUser = 'rowlanja'
labels = []
values = []
dates = []
commits= []
colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

app= Flask(__name__)
@app.route('/')
def home():
    return render_template('homePage.html')



@app.route('/', methods=['POST'])
def userPost():
    text = request.form.get('username')

    #GETTING USER PROFILE INFO
    user_request = requests.get('https://api.github.com/users/'+text, auth=(token_AuthUser, api_token)).json()
    name = user_request["login"]
    location = user_request["location"]
    company = user_request["company"]
    hireable = user_request["hireable"]
    email = user_request["email"]
    bio = user_request["bio"]
    twitter_username = user_request["twitter_username"]
    followers = user_request["followers"]
    following = user_request["following"]
    created_at = user_request["created_at"]
    created_at = dateutil.parser.parse(created_at)
    created_at = created_at.date().strftime("%d/%m/%Y")
    blog = user_request["blog"]

    #GETTING Programming LANGUAGES USED INFO
    #PUTS LANGUAGES IN LABELS LIST
    #PUT LANGUAGE USED COUNT IN VALUES LIST
    user_request = requests.get('https://api.github.com/users/'+text+"/repos", auth=(token_AuthUser, api_token)).json()
    languageDict = {}
    for val in user_request :
        if(val["language"] != None) : 
            languageDict[val["language"]] = languageDict.get(val["language"], 0) + 1
            random_number = random.randint(0,16777215)
            hex_number = str(hex(random_number))
            hex_number ='#'+ hex_number[2:]
            colors.append(hex_number)
    labels = languageDict.keys()
    values = languageDict.values()

    #GETTING COMMIT HISTORY
    #PUTS DATES IN DATES LIST
    #PUT COMMIT COUNT IN COMMITS LIST
    user_request = requests.get('https://api.github.com/users/'+text+"/events", auth=(token_AuthUser, api_token)).json()
    for entry in user_request :
        x = entry["payload"]
        if "commits" in x :
            size = len(x["commits"])
            yourdate = dateutil.parser.parse(entry["created_at"])
            yourdate = yourdate.date().strftime("%d/%m/%Y")
            dates.append(yourdate)
            commits.append(size)
            maxCommitCount = max(commits)
    #GETTING USER COMMIT TIMES TO PLOT WHEN USER IS MOST ACTIVE DURING THE DAY
    commitTimeData = getTimes(user_request) 
    userActivityData = deriveActivityInfo(commitTimeData)
    print(userActivityData)
    maxCommitActivity = max(commitTimeData.values()) + 3
    repoLanguages=getLanguages(text)
    repoLanguages = sorted(repoLanguages.items(), key= lambda x: len(x[1]))
    repoLanguages = dict(repoLanguages)

    
    return render_template('user.html',
        name = name, location = location,
        company = company, hireable = hireable,
        email = email,  bio = bio,
        twitter_username = twitter_username, followers = followers,
        following = following,  created_at = created_at,
        blog = blog,  max=1, set=zip( values, labels, colors),
        labelsLine=dates, valuesLine=commits, 
        followersList=getFollowers(text), repoLanguages=repoLanguages, commitTimeData=commitTimeData,
        maxCommitActivity=maxCommitActivity, userActivityData = userActivityData
   )

#GETS THE LIST OF FOLLOWERS OF A USER
def getFollowers(userName):
    user_request = requests.get('https://api.github.com/users/'+userName+"/followers", auth=(token_AuthUser, api_token)).json()
    followers = {}
    for user in user_request : 
        followers[user["login"]]= user["html_url"]
    
    return followers

# GETS THE REPOS % LANGUAGES USED
# THE IF STATEMENT CHECK WHETHER THE LANGUAGE KEY IS SET TO A VALUE IN THE REPOS API RESPONSE
# IF THE REPO HAS MULTIPLE LANGUAGES THIS VLAUE IS NULL AND THE LANGUAGES ARE STORED AT THE /REPO/LANGUAGES API ENPOINT
# IF THE REPO HAS A SINGLE VALUE THEN THE LANGUAGE WILL BE DIRECTLY STORED ON THE /REPOS API ENPOINT
def getLanguages(userName):
    user_request = requests.get('https://api.github.com/users/'+userName+"/repos", auth=(token_AuthUser, api_token)).json()
    repoLanguages = {}
    for repo in user_request :
        if repo["language"] :
            language_request = requests.get('https://api.github.com/repos/'+repo["full_name"]+"/languages", auth=('rowlanja', api_token)).json()
            repoLanguages[repo["name"]] = language_request
        elif repo["language"] and not(repo["language"] is None):
            repoLanguages[repo["name"]] = repo["language"]
    return repoLanguages

def getUserInfo(text):
    user_request = requests.get('https://api.github.com/users/'+text, auth=(token_AuthUser, api_token)).json()
    userProfile = {}
    userProfile["name"] = user_request["login"]
    userProfile["location"] = user_request["location"]
    userProfile["company"] = user_request["company"]
    userProfile["hireable"] = user_request["hireable"]
    userProfile["email"] = user_request["email"]
    userProfile["bio"] = user_request["bio"]
    userProfile["twitter_username"] = user_request["twitter_username"]
    userProfile["followers"] = user_request["followers"]
    userProfile["following"] = user_request["following"]
    created_at = user_request["created_at"]
    created_at = dateutil.parser.parse(created_at)
    created_at = created_at.date().strftime("%d/%m/%Y")
    userProfile["created_at"] = created_at
    userProfile["blog"] = user_request["blog"]
    return userProfile



@app.route('/repoGet', methods=['POST'])
def repoGet():
    username = request.form.get('userName')
    reponame = request.form.get('repoName')
    user_request = requests.get('https://api.github.com/users/'+username, auth=(token_AuthUser, api_token)).json()
    repo_request = requests.get('https://api.github.com/repos/'+username+"/"+reponame, auth=(token_AuthUser, api_token)).json()
    language_request = requests.get('https://api.github.com/repos/'+username+"/"+reponame+"/languages", auth=(token_AuthUser, api_token)).json()
    commit_request = requests.get('https://api.github.com/repos/'+username+"/"+reponame+"/commits", auth=(token_AuthUser, api_token)).json()
    yourdate = dateutil.parser.parse(repo_request["created_at"]) 
    yourdate = yourdate.date().strftime("%d/%m/%Y")
    languages=[]
    lines=[]
    #THIS POPULATES THE LANGUAGE ANALYSIS DATA
    for key, value in language_request.items() :
        languages.append(key)
        lines.append(value)
    #THIS CREATES A LEADERBOARD FOR COMMITERS
    commiters = {}
    for commit in commit_request:
        commiters[commit["author"]["login"]] = commiters.get(commit["author"]["login"], 0) + 1
    commitUser = []
    commitCount = []
    commitColors = []
    for key, value in commiters.items():
        newKey = str(key)
        commitUser.append(newKey)
        commitCount.append(value)
        rgb1 = str(random.randint(0,255))
        rgb2 = str(random.randint(0,255))
        rgb3 = str(random.randint(0,255))
        rgbStr = 'rgb('+rgb1+','+ rgb2+','+rgb3+')'
        commitColors.append(rgbStr)
    commitData = retrieveCommitHistory(commit_request)
    barData = zip()
    return render_template('project.html', title = username, reponame = reponame,
    name=repo_request["name"], created_at=yourdate, stargazers_count=repo_request["stargazers_count"],
    watchers_count=repo_request["watchers_count"],forks_count=repo_request["forks_count"],open_issues_count=repo_request["open_issues_count"],
    license = repo_request["license"]["key"],  commit_count = len(commit_request),
    lines = lines, languages = languages, commiters = commiters, description = repo_request["description"],
    userProfile = getUserInfo(username), commitCount = commitCount, commitUser =  commitUser,  commitColors = commitColors, colors = colors,
    commitData = commitData 
    )

def getTimes(dataSet) :
    
    commitTimes = {
        "08:00" : 0, "09:00" : 0, "10:00" : 0,
        "11:00" : 0, "12:00" : 0, "13:00" : 0,
        "14:00" : 0, "15:00" : 0, "16:00" : 0,
        "17:00" : 0, "18:00" : 0, "19:00" : 0,
        "20:00" : 0, "21:00" : 0, "22:00" : 0,
        "23:00" : 0, "00:00" : 0, "01:00" : 0, 
        "02:00" : 0, "03:00" : 0, "04:00" : 0,
        "05:00" : 0, "06:00" : 0, "07:00" : 0    
    } 
    #INITIALIZING HOURS FROM 0 TO 24 WITH VALUES 0
 
    for n in range(23):
        n = '%02d' % n
        commitTimes[str(n)+":00"] = 0
    for entry in dataSet :
        if entry["type"] == "PushEvent" :
            commitSection = entry["payload"]
            commitCount =  len(commitSection["commits"])
            created_at = entry["created_at"]
            created_at = dateutil.parser.parse(created_at)
            created_at = created_at.time().hour
            commitSize = len(commitSection["commits"])
            commitTimes[str(created_at)+":00"] = commitTimes.get(created_at, commitSize) + 1
    return commitTimes

## CURRENT WORKING SECTION
def deriveActivityInfo(commitTimes) : 
    description = {}
    found = False
    earliestTime = ""
    latestTime = ""
    peakTime = "00:00"
    peakValues = 0
    for key, value in commitTimes.items() : 
        timeInt = int(key[0:2])
        if(value > peakValues) :
            peakTime = key
            peakValues = value
        if(found == False and value != 0) : 
            earliestTime = key
            found = True
        if(value != 0) : 
            latestTime = key


    description[" Earliest commit Time "] = earliestTime
    description[" Latest working Time  "] = latestTime
    description[" Activity Peak  "] = "This users peak time was " + peakTime + " with a value of : " + str(peakValues)
    if(int(earliestTime[0:2]) < 12) :
        description["Early Working Time Information"] = "This user is good at working in the morning"
    else : description["Early Working Time Information"] = " This user does not like to work in the morning"
    if(int(latestTime[0:2]) > 18) : 
        description["Late Working Time Information"] = "This user is likes working in the evening"
    else : description["Late Working Time Information"] = "This user doesnt like working in the evening"
    if(int(latestTime[0:2]) - int(earliestTime[0:2]) > 4) :
        description["Work time range information"] = "this user works at a variety of times"
    else : description["Work time range information"] = "this user prefers working at the same time everyday"
    return description

def retrieveCommitHistory(commit_request) :
    commitHistory = []
    for entry in commit_request : 
        date = entry["commit"]["author"]["date"]
        yourdate = dateutil.parser.parse(date) 
        yourdate = yourdate.date().strftime("%d/%m/%Y")
        commitHistory.append(yourdate)

    returnedData = {}
    for entry in commitHistory :
        count = commitHistory.count(entry)
        returnedData[entry] = count
    return returnedData
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001) 
