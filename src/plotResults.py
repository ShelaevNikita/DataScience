#!/usr/bin/env python3
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html
from dash.dependencies import Input, Output

class PlotResults():

    FilterKeys = ['Количество игр по жанрам',
                  'Количество игр по платформам',
                  'Жанры игр по платформам',
                  'Игры с самым высоким рейтингом',
                  'Количество игр по их годам выхода',
                  'Игры с самым большим количеством отзывов']

    def __init__(self, datapath):
        self.datapath = datapath

        self.app = Dash(__name__)
    
    def getResults(self):

        with open(self.datapath, 'r', encoding = 'utf-8') as file:
            resultJSON = json.loads(file.read())

        return resultJSON

    def numberGenre(self, resultJSON):

        table = pd.DataFrame(resultJSON['number_by_genre'].items(), columns = ['Genre', 'Value'])
        table = table.sort_values(by = 'Value', ascending = False)

        allNumbers = table['Value'].sum()
        return (table, allNumbers)

    def numberPlatform(self, resultJSON):

        table = pd.DataFrame(resultJSON['number_by_platform'].items(), columns = ['Platform', 'Count'])

        allNumbers = table['Count'].sum()
        return (table, allNumbers)

    def highestScored(self, resultJSON):

        table = pd.DataFrame(resultJSON['highest_scored'].items(), columns = ['Game', 'Score'])

        return table

    def numberYears(self, resultJSON):

        table = pd.DataFrame(resultJSON['number_by_years'].items(), columns = ['Year', 'Games'])
        table = table.sort_values(by = 'Year')

        allNumbers = table['Games'].sum()

        return (table, allNumbers)

    def highReviewed(self, resultJSON):
        
        table = pd.DataFrame(resultJSON['high_reviewed_games'].items(), columns = ['Game', 'Reviews'])

        return table
    
    def platformGenre(self, resultJSON):

        platforms = ['PC', 'PlayStation 5', 'PlayStation 4', 'Xbox Series X/S', 'Xbox One', 'Nintendo Switch']

        tables = []
        for platform in platforms:
            table = pd.DataFrame(resultJSON['number_per_platform_by_genre'][platform].items(),
                                 columns = ['Genre', 'Value'])
            table = table.sort_values(by = 'Value', ascending = False)
            tables.append((platform, table))

        return tables

    def layout(self, resultJSON):

        numberGenre, allNumbers = self.numberGenre(resultJSON)

        self.app.layout = html.Div([
            html.Div([
                dcc.Dropdown(
                    self.FilterKeys,
                    self.FilterKeys[0],
                    id = 'xaxis-column'
                )], style = {'width':'50%', 'float':'center', 'display':'inline-block'}),
            dcc.Graph(id = 'indicator-graphic'),
        ])

        @self.app.callback(
            Output('indicator-graphic', 'figure'),
            Input('xaxis-column', 'value'))
        def update_graph(filter):

            if filter == self.FilterKeys[0]:

                numberGenre, allNumbers = self.numberGenre(resultJSON)

                fig = px.bar(numberGenre, x = 'Genre', y = 'Value',
                             title = f'Количество игр по жанрам (Всего: {allNumbers})', text = 'Value')
                fig.update_layout(yaxis_title = 'Количество игр', xaxis_title = 'Название жанра')

            elif filter == self.FilterKeys[1]:

                numberPlatform, allNumbers = self.numberPlatform(resultJSON)

                fig = px.pie(numberPlatform, names = 'Platform', values = 'Count',
                             title = 'Количество игр по платформам', hole = 0.5)
                fig.update_layout(annotations = [dict(text = f'Всего = {allNumbers}',
                                                      x = 0.5, y = 0.5, font_size = 18, showarrow = False)])
            
            elif filter == self.FilterKeys[2]:

                platformGenre = self.platformGenre(resultJSON)

                fig = go.Figure()
                for elem in platformGenre:
                    fig.add_trace(go.Bar(y = elem[1]['Value'], x = elem[1]['Genre'], name = elem[0]))
                fig.update_layout(title = 'Жанры игр по платформам',
                                  xaxis_title = 'Жанры',
                                  yaxis_title = 'Количество игр')

            elif filter == self.FilterKeys[3]:

                highestScored = self.highestScored(resultJSON)

                fig = px.histogram(highestScored, x = 'Game', y = 'Score', title = 'Игры с самым высоким рейтингом (Top-15)',
                                   )
                fig.update_layout(xaxis_title = 'Название игры', yaxis_title = 'Рейтинг')

            elif filter == self.FilterKeys[4]:

                gameYears, allNumbers = self.numberYears(resultJSON)

                fig = px.bar(gameYears, x = 'Year', y = 'Games',
                             title = f'Количество игр по их годам выхода (всего игр: {allNumbers})', text = 'Games')
                fig.update_layout(yaxis_title = 'Количество игр', xaxis_title = 'Год выхода')

            elif filter == self.FilterKeys[5]:

                highReviewed = self.highReviewed(resultJSON)

                fig = px.histogram(highReviewed, x = 'Game', y = 'Reviews',
                                   title = 'Игры с самым большим количеством отзывов (Top-15)')
                fig.update_layout(xaxis_title = 'Название игры', yaxis_title = 'Количество отзывов')

            fig.update_layout(title_x = 0.5, autosize = False, width = 1500, height = 700)
            return fig

    def main(self):
        resultJSON = self.getResults()
        self.layout(resultJSON)
        self.app.run_server()

if __name__ == '__main__':
    dataPath = './data/result.json'
    PlotResults(dataPath).main()
