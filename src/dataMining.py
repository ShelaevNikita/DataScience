#!/usr/bin/env python3
import requests
import json
import threading
import re
 
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs

class DataMining(object):

    Month = {'января':'01', 'февраля':'02', 'марта':'03', 'апреля':'04', 'мая':'05', 'июня':'06',
            'июля':'07', 'августа':'08', 'сентября':'09', 'октября':'10', 'ноября':'11', 'декабря':'12'}

    Proxies = {'http':'http://10.10.1.10:3128',
               'https':'http://10.10.1.10:1080'}

    def __init__(self, datapath, threads):
        self.datapath = datapath
        self.threads = threads

        self.openCriticURL = 'https://opencritic.com/game/'
        self.metarankingURL = 'https://metarankings.ru/reviews/'

        self.lock = threading.Lock()

        self.IDSkipped = []
        self.IDRU = []
        self.games = []
        self.IDMax = 0
    
    def urlParsing(self, IDArray):

        lock = threading.Lock()

        for id in IDArray:

            # with self.lock:
                # print('\t ID =', id)

            try:
                responseEN = requests.get(self.openCriticURL + f'{id}/reviews')
            except requests.ConnectionError:
                with self.lock:
                    self.IDSkipped.append(id)
                continue

            if responseEN.status_code != 200:
                with self.lock:
                    self.IDSkipped.append(id)
                continue

            pageCriticsEN = bs(responseEN.content, 'html.parser')
            jsonFind = pageCriticsEN.find('script', type = 'application/ld+json').text
            if jsonFind != '':        
                dataJSON = json.loads(jsonFind)
            else:
                with self.lock:
                    self.IDSkipped.append(id)
                continue

            with self.lock:
                if id > self.IDMax:
                    self.IDMax = id

            gameName = dataJSON['url'].split('/')[3]

            game = {'id'         :id,
                    'name'       :dataJSON['name'],
                    'platform'   :dataJSON['gamePlatform'], 
                    'genre'      :dataJSON['genre'], 
                    'dataRelized':dataJSON['datePublished'].split('T')[0]}

            if 'description' in dataJSON: 
                game['description'] = dataJSON['description']
            else: 
                game['description'] = []

            if 'image' in dataJSON: 
                game['image'] = dataJSON['image']
            else:
                if dataJSON['screenshot']:
                    game['image'] = dataJSON['screenshot'][0]
                else:
                    game['image'] = []
        
            if 'publisher' in dataJSON:
                publisher = [elem['name'] for elem in dataJSON['publisher']]
                game['publisher'] = publisher
            else:
                publisher = False

            if 'author' in dataJSON:
                author = [elem['name'] if 'name' in elem else '' for elem in dataJSON['author']]
                game['author'] = author
            else:
                author = False
        
            if author and not publisher:
                game['publisher'] = author
            if not author and publisher:
                game['author'] = publisher
         
            rating = {'EN':{}, 'RU':{ 'critics':{}, 'gamers':{} } }

            reviewsEN = []
            scoreArr = []

            reviewURL = self.openCriticURL + f'{id}/' + gameName + '/reviews?sort=popularity'
            
            i = 0
            flagStop = False

            while not flagStop:

                i += 1

                if i > 1:
                    reviewURLNext = reviewURL + f'&page={i}'
                else:
                    reviewURLNext = reviewURL

                try:
                    responseReview = requests.get(reviewURLNext)
                except requests.ConnectionError:
                    with self.lock:
                        self.IDSkipped.append(id)
                    continue

                if responseReview.status_code != 200:
                    with self.lock:
                        self.IDSkipped.append(id)
                    continue

                pageReviews = bs(responseReview.content, 'html.parser')

                next = pageReviews.find('a', class_ = 'btn')
                if not next is None and next.text.strip() == 'Next':
                    flagStop = False
                else:
                    flagStop = True

                for elem in pageReviews.findAll('app-review-row'):

                    reviewDate = elem.find('div', class_ = 'text-right date-block').text
                    key = reviewDate.split(' ')[2]
                    keyInt = int(key)
                    if keyInt > 2000:
                        date = dt.strptime(reviewDate, '%b %d, %Y')
                    elif keyInt < 100:
                        date = dt.strptime(reviewDate, '%b %d, %y')
                    else:
                        reviewDate = reviewDate.replace(key, game['dataRelized'].split('-')[0])
                        date = dt.strptime(reviewDate, '%b %d, %Y')

                    dateString = f'{date}'.split()[0]

                    reviewScore = elem.find('span', class_ = 'score-number-bold')
                    if reviewScore:
                        scoreText = reviewScore.text
                        score = 0
                        flag = scoreText.split('/')
                        if len(flag) == 2:
                            first  = re.sub(r"[^\d.]", '', flag[0])
                            second = re.sub(r"[^\d.]", '', flag[1])
                            if first != '' and second != '':
                                try:
                                    score = round(float(first) / float(second), 3)
                                    scoreArr.append(score)
                                except ValueError:
                                    pass
                        elif scoreText.strip()[-1] == '%':
                            score = int(scoreText[:-1]) / 100
                            scoreArr.append(score)
                    else:
                        scoreText = 'AllStars!'
                        score = 0
        
                    reviewText = elem.find('p', class_ = 'mb-0 wspw')
                    if reviewText:
                        reviewText = reviewText.text
                    else:
                        reviewText = ''

                    reviewsArray = elem.findAll('a', class_ = 'deco-none')
                    if len(reviewsArray) < 3:
                        organization = reviewsArray[1].text
                        author = elem.find('span', class_ = 'author-name').text
                    else:
                        author = reviewsArray[1].text
                        organization = reviewsArray[2].text

                    review = {'organization':organization, 
                              'author'      :author, 
                              'date'        :dateString,
                              'scoreText'   :scoreText, 
                              'score'       :score, 
                              'reviewText'  :reviewText}

                    reviewsEN.append(review)
            
            if 'aggregateRating' in dataJSON:
                ratingValue = dataJSON['aggregateRating']['ratingValue']
                count = dataJSON['aggregateRating']['reviewCount']
            else:
                ratingValue = 0.0
                count = len(reviewsEN)

            if ratingValue == 0.0 and len(scoreArr) > 0:
                ratingValue = round(sum(scoreArr) / len(scoreArr), 3) * 100

            rating['EN'] = {'ratingValue':ratingValue,
                            'count'      :count, 
                            'reviews'    :reviewsEN}

            try:
                responseRU = requests.get(self.metarankingURL + gameName)
            except requests.exceptions.RequestException:
                game['rating'] = rating
                with self.lock:
                    self.games.append(game)
                continue

            if responseRU.status_code != 200:
                game['rating'] = rating
                with self.lock:
                    self.games.append(game)
                continue

            pageMetarating = bs(responseRU.content, 'html.parser')

            with self.lock:
                self.IDRU.append(id)

            reviewArrayCriticsRU = pageMetarating.findAll('div', class_ = 'critic-text')

            reviewsCriticsRU = []
            scoreArray = []

            for elem in reviewArrayCriticsRU:
                scoreText = elem.find('span', class_ = 'tooltip')
                score = 0
                if scoreText:
                    try:
                        score = float(scoreText.text)
                        scoreArray.append(score)
                    except ValueError:
                        pass                   
                criticText = elem.findAll('p')
                auth = criticText[0].text.split(' ', 1)

                review = {'organization':auth[0],
                          'author'      :(auth[1].split(':')[1]).strip(),
                          'score'       :score,
                          'reviewText'  :criticText[1].text}

                reviewsCriticsRU.append(review)
        
            if len(scoreArray) > 0:
                ratingValue = round(sum(scoreArray) / len(scoreArray), 3)
            else:
                ratingValue = 0

            count = len(reviewArrayCriticsRU)

            rating['RU']['critics'] = {'ratingValue':ratingValue,
                                       'count'      :count,
                                       'reviews'    :reviewsCriticsRU}

            reviewArrayGamers = pageMetarating.findAll('div', class_ = 'ureview-text')

            reviewsGamersRU = []
            scoreArray = []

            for elem in reviewArrayGamers:
                scoreText = elem.find('span', class_ = 'tooltip')
                if scoreText:
                    try:
                        score = float(scoreText.text)
                        scoreArray.append(score)
                    except ValueError:
                        pass
                else:
                    break

                criticText = elem.findAll('p')
                flag = criticText[1].text.split(':')
                if len(flag) == 2:
                    reviewDate = (flag[1]).strip()
                    key = reviewDate.split(' ')[1]
                    reviewDate = reviewDate.replace(key, self.Month[key]) 
                    reviewDateFormat = dt.strptime(reviewDate, '%d %m %Y')
                else:
                    reviewDate = flag[0].strip()
                    reviewDateFormat = dt.strptime(reviewDate, '%d.%m.%Y')

                review = {'author'    :criticText[0].text,
                          'date'      :f'{reviewDateFormat}'.split()[0],
                          'score'     :score,
                          'reviewText':criticText[2].text}

                reviewsGamersRU.append(review)
        
            count = len(scoreArray)

            if count > 0:
                ratingValue = round(sum(scoreArray) / count, 3)
            else:
                ratingValue = 0

            rating['RU']['gamers'] = {'ratingValue':ratingValue,
                                      'count'      :count,
                                      'reviews'    :reviewsGamersRU}

            game['rating'] = rating
            with self.lock:
                self.games.append(game)

        return

    def main(self):

        print(f'\n\t Данные скачиваются в этот файл: {self.dataPath}')

        parts = self.threads

        idArrays = [list(range(1, 14151, 1))[i::parts] for i in range(parts)]

        threadArray = []
        for i in range(parts):
            thr = threading.Thread(target = self.urlParsing, args = (idArrays[i],))
            threadArray.append(thr)
            thr.start()
        
        for thr in threadArray:
            thr.join()
                       
        dateNow = dt.today()
        dateNowText = f'{dateNow}'.split(' ')[0]

        dataJSON = {'dateModified':dateNowText, 
                    'IDSkipped'   :self.IDSkipped,
                    'IDMax'       :self.IDMax,
                    'IDRU'        :self.IDRU,
                    'games'       :self.games}

        with open(self.datapath, 'w', encoding = 'utf-8') as file:
            json.dump(dataJSON, file, indent = 4, ensure_ascii = False, separators = (',', ': '))
        
        print('\n\t Ура!!! Данные успешно скачались')

        return

if __name__ == '__main__':
    dataPath = './data/data.json'
    threads = 4
    DataMining(dataPath, threads).main()
