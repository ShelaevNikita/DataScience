#!/usr/bin/env python3

import src.plotResults
import src.dataMining
import src.dataAnalytics

def main():

    dataPathFrom = './data/data.json'
    dataPathTo = './data/result.json'

    print('\n\t Добро пожаловать в исследование по Opencritic/MetaRankings! :)')

    flagDownload = input('\n\t Вы хотите скачать данные? (Y / N): > ')
    if flagDownload.lower().startswith('y'):      
        threads = 4
        src.dataMining.DataMining(dataPathFrom, threads).main()
    
    flagAnalytics = input('\n\t Хотите ли Вы обработать скачанные данные? (Y / N): > ')
    if flagAnalytics.lower().startswith('y'):
        src.dataAnalytics.DataAnalytics(dataPathFrom, dataPathTo).main()

    flagPlotResults = input('\n\t И последний вопрос: вы хотите увидеть результаты обработки данных? (Y / N): > ')
    if flagPlotResults.lower().startswith('y'):       
        src.plotResults.PlotResults(dataPathTo).main()

    print('\n\t До скорых встреч! Надеюсь, Вам понравилось)')

    return

if __name__ == '__main__':
    main()