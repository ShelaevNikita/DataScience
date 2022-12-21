#!/usr/bin/env python3
import os

import src.plotResults
import src.dataMining

def main():
    print('\n\t Добро пожаловать в исследование по Opencritic/MetaRankings! :)')

    flagDownload = input('\n\t Вы хотите скачать данные? (Y / N): > ')
    if flagDownload.lower().startswith('y'):
        dataPath = './data/data.json'
        threads = 4
        src.dataMining.DataMining(dataPath, threads).main()
    
    flagAnalytics = input('\n\t Хотите ли Вы обработать скачанные данные? (Y / N): > ')
    if flagAnalytics.lower().startswith('y'):
        rbFile = dataAnalytics.rb
        os.system(f'ruby {rbFile}')

    flagPlotResults = input('\n\t И последний вопрос: вы хотите увидеть результаты обработки данных? (Y / N): > ')
    if flagPlotResults.lower().startswith('y'):
        dataPath = './data/result.json'
        src.plotResults.PlotResults(dataPath).main()

    print('\n\t До скорых встреч! Надеюсь, Вам понравилось)')

    return

if __name__ == '__main__':
    main()