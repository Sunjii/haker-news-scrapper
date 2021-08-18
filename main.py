from threading import active_count
import requests
from flask import Flask, render_template, request

base_url = "http://hn.algolia.com/api/v1"

# This URL gets the newest stories.
new = f"{base_url}/search_by_date?tags=story"

# This URL gets the most popular stories
popular = f"{base_url}/search?tags=story"


# This function makes the URL to get the detail of a storie by id.
# Heres the documentation: https://hn.algolia.com/api
def make_detail_url(id):
  return f"{base_url}/items/{id}"

db_new = {}
db_pop = {}
app = Flask("DayNine")


## new 추출하여 리스트로 만들자.
    # 우리가 필요한 것은 id, title, link, point, writer, comment_count 이다.
    # API에서 이는 각각 
    # objectID, title, url, points, author, num_comments 이다.  -- // objectID는 make_detail_url(id) 에 쓰인다.
    # 원한다면 created_at 으로 기사 작성 날짜를 가져올 수 있음.

    # /<id> page에서 필요한 내용은
    # title, points, author, link,
    # 본문의 내용과 코멘트 리스트는
    # make_detail_url(id) 함수를 통해 얻을 수 있음
# 해당 주소의 json에서 children : [ {coment1}, {coment2}, ... ] 이다.
    # comment의 정보는 author, text 이다. null인 경우는 삭제된 코멘트이다.
    # 원한다면 created_at 을 통해 코멘트 작성 날짜도 가져올 수 있음.


def extract_news(api_url, flag):
    result = requests.get(api_url)
    get_json = result.json()
    news_list = get_json['hits']
    
    for news in news_list:
        ID = news['objectID']
        ex_news = {
            'objectID' : news['objectID'],
            'title' : news['title'],
            'url': news['url'],
            'points' : news['points'],
            'author' : news['author'],
            'num_comments' : news['num_comments']
        }
        if(flag == "new"):
            db_new[ID] = ex_news
        else:
            db_pop[ID] = ex_news
            
    return

extract_news(new, "new")
extract_news(popular, "popular")
db_new.update(db_pop)



@app.route("/")
def home():
    order = request.args.get('order_by')
    if order == "new":
        return render_template("new_index.html", news_list=db_new)
    elif order == "popular":
        return render_template("index.html", news_list=db_pop)
    elif order is None:
        return render_template("index.html", news_list=db_pop)
    else:
        return "Not found"






@app.route("/<id>")
def news(id):
    result = requests.get(make_detail_url(id))
    get_json = result.json()
    
    try:
        if get_json['status']: # error가 있는 경우
            return f"ID : {id} is {get_json['status']}."
    except:
        pass

    aticle = {
        'title' : get_json['title'],
        'created_at' : get_json['created_at'],
        'points' : get_json['points'],
        'author' : get_json['author'],
        'url' : get_json['url'],
        'type' : get_json['type'],
        'text' : get_json['text'],
        'childern' : get_json['children']
    }
    if aticle['text'] is None:
        aticle['text'] = ""
    if aticle['url'] is None:
        aticle['url'] = ""
    for c in aticle['childern']:
        if c['author'] is None:
            aticle['childern'].remove(c)


    return render_template("detail.html", news_id=id, aticle = aticle)


app.run(host="0.0.0.0")