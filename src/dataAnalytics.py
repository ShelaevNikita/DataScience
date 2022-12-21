#!/usr/bin/env python3
import json

class DataAnalytics():

    def __init__(self, dataPathFrom, dataPathTo):
        self.dataPathFrom = dataPathFrom
        self.dataPathTo   = dataPathTo

    def countNumber(self, resultJSON, key):
        resultDict = {}
        for game in resultJSON:
            for elem in game[key]:
                if elem in resultDict:
                    resultDict[elem] += 1
                else:
                    resultDict[elem] = 0
        return resultDict

    def sortByCount(self, elem):
        return elem[1]

    def sortByValue(self, elem):
        return elem[2]

    def countYear(self, resultJSON):
        resultDict = {}
        for game in resultJSON:
            elem = game['dataRelized']
            year = int(elem.split('-')[0])
            if year in resultDict:
                resultDict[year] += 1
            else:
                resultDict[year] = 0
        return resultDict

    def platformGenres(self, resultJSON, numberPlatform):
        resultDict = {}
        for key, _ in numberPlatform.items():
            keyDict = {}
            for game in resultJSON:
                if not key in game['platform']:
                    continue
                for elem in game['genre']:
                    if elem in keyDict:
                        keyDict[elem] += 1
                    else:
                        keyDict[elem] = 0
            resultDict[key] = keyDict
        return resultDict

    def main(self):
        with open(self.dataPathFrom, 'r', encoding = 'utf-8') as file:
            resultJSON = json.loads(file.read(), strict = False)['games']

        gamesTotalNumber = len(resultJSON)

        numberGenre    = self.countNumber(resultJSON, 'genre')
        numberPlatform = self.countNumber(resultJSON, 'platform')

        resultArray = []
        for game in resultJSON:
            resultArray.append((game['name'], game['rating']['EN']['count'],
                              game['rating']['EN']['ratingValue']))
        resultArray = list(filter(lambda x: x[1] >= 10, resultArray))

        highScoreGamesList = sorted(resultArray, key = self.sortByValue)[-15:]
        highScoreGames = {elem[0]:elem[2] for elem in highScoreGamesList}

        highReviewGamesList = sorted(resultArray, key = self.sortByCount)[-15:]
        highReviewGames = {elem[0]:elem[1] for elem in highReviewGamesList}

        numberYear = self.countYear(resultJSON)

        platformGenre = self.platformGenres(resultJSON, numberPlatform)

        dataJSON = {'total_number'                :gamesTotalNumber, 
                    'number_by_genre'             :numberGenre,
                    'number_by_platform'          :numberPlatform,
                    'highest_scored'              :highScoreGames,
                    'number_by_years'             :numberYear,
                    'high_reviewed_games'         :highReviewGames,
                    'number_per_platform_by_genre':platformGenre}

        with open(self.dataPathTo, 'w', encoding = 'utf-8') as file:
            json.dump(dataJSON, file, indent = 4, ensure_ascii = False, separators = (',', ': '))

        return

if __name__ == '__main__':
    dataPathFrom = './data/data.json'
    dataPathTo   = './data/result.json'
    DataAnalytics(dataPathFrom, dataPathTo).main()
