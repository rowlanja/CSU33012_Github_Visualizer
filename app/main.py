from flask import Flask, redirect, request, render_template
import requests
import json
import random
import dateutil.parser
import datetime


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
def my_form_post():
    text = request.form.get('username')

    #GETTING USER PROFILE INFO
    user_request = requests.get('https://api.github.com/users/'+text, auth=('rowlanja', '72f894a6faa4ee1fd6cee8b51bb722d6587a0601')).json()
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
    user_request = requests.get('https://api.github.com/users/'+text+"/repos", auth=('rowlanja', '72f894a6faa4ee1fd6cee8b51bb722d6587a0601')).json()
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
    user_request = requests.get('https://api.github.com/users/'+text+"/events", auth=('rowlanja', '72f894a6faa4ee1fd6cee8b51bb722d6587a0601')).json()
    for entry in user_request :
        x = entry["payload"]
        if "commits" in x :
            size = len(x["commits"])
            yourdate = dateutil.parser.parse(entry["created_at"])
            yourdate = yourdate.date().strftime("%d/%m/%Y")
            dates.append(yourdate)
            commits.append(size)
            maxCommitCount = max(commits)


    repoLanguages=getLanguages(text)

    repoLanguages = sorted(repoLanguages.items(), key= lambda x: len(x[1]))
    repoLanguages = dict(repoLanguages)
    print("sorted", repoLanguages)
    #print(getLanguages(text))
    return render_template('user.html',
        name = name, location = location,
        company = company, hireable = hireable,
        email = email,  bio = bio,
        twitter_username = twitter_username, followers = followers,
        following = following,  created_at = created_at,
        blog = blog, title='Bitcoin Monthly Price in USD', max=1, set=zip( values, labels, colors),
        labelsLine=dates, valuesLine=commits, 
        followersList=getFollowers(text), repoLanguages=repoLanguages
   )

#GETS THE LIST OF FOLLOWERS OF A USER
def getFollowers(userName):
    user_request = requests.get('https://api.github.com/users/'+userName+"/followers", auth=('rowlanja', '72f894a6faa4ee1fd6cee8b51bb722d6587a0601')).json()
    followers = {}
    for user in user_request : 
        followers[user["login"]]= user["html_url"]
    
    return followers

# GETS THE REPOS % LANGUAGES USED
# THE IF STATEMENT CHECK WHETHER THE LANGUAGE KEY IS SET TO A VALUE IN THE REPOS API RESPONSE
# IF THE REPO HAS MULTIPLE LANGUAGES THIS VLAUE IS NULL AND THE LANGUAGES ARE STORED AT THE /REPO/LANGUAGES API ENPOINT
# IF THE REPO HAS A SINGLE VALUE THEN THE LANGUAGE WILL BE DIRECTLY STORED ON THE /REPOS API ENPOINT
def getLanguages(userName):
    user_request = requests.get('https://api.github.com/users/'+userName+"/repos", auth=('rowlanja', '72f894a6faa4ee1fd6cee8b51bb722d6587a0601')).json()
    repoLanguages = {}
    for repo in user_request :
        if repo["language"] :
            language_request = requests.get('https://api.github.com/repos/'+repo["full_name"]+"/languages", auth=('rowlanja', '72f894a6faa4ee1fd6cee8b51bb722d6587a0601')).json()
            repoLanguages[repo["name"]] = language_request
        elif repo["language"] and not(repo["language"] is None):
            repoLanguages[repo["name"]] = repo["language"]
    return repoLanguages

@app.route('/linechart')
def line():
    line_labels=labels
    line_values=values
    return render_template('linechart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=line_labels, values=line_values)

if __name__ == '__main__':
    app.run(threaded=True, port=5000)