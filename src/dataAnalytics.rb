# frozen_string_literal: true

require 'json'
require 'date'
require 'csv'
require "set"

data = JSON.parse(File.read('./data/data.json'))['games']

games_total_number = data.count

genres = data.each_with_object([]) { |game, acc| acc.concat(game['genre']) }.uniq
number_by_genre = Hash[genres.map { |genre| [genre, data.select { |game| game['genre'].include?(genre) }.count] }]

platforms = data.each_with_object([]) { |game, acc| acc.concat(game['platform']) }.uniq
number_by_platform = Hash[platforms.map { |platform| [platform, data.select { |game| game['platform'].include?(platform) }.count] }]

high_scored_games = data
                    .select { |game| game['rating']['EN']['reviews'].count > 2 }
                    .sort_by { |game| game['rating']['EN']['ratingValue'] }
                    .reverse[0..9]
                    .each_with_object({}) { |game, hash| hash[game['name']] = game['rating']['EN']['ratingValue'] }

years = data.each_with_object([]) { |game, acc| acc << Date.parse(game['dataRelized']).year }.uniq
games_per_year = Hash[years.map { |year| [year, data.select { |game| Date.parse(game['dataRelized']).year.eql?(year) }.count] }]

high_reviewed_games = data
                      .sort_by { |game| game['rating']['EN']['reviews'].count }
                      .reverse[0..9]
                      .each_with_object({}) { |game, hash| hash[game['name']] = game['rating']['EN']['reviews'].count }

authors = data.each_with_object([]) { |game, acc| acc.concat(game['author']) }.uniq
authors_games_number = Hash[authors.map { |author| [author, data.select { |game| game['author'].include?(author) }.count] }]

platform_genres_number = {}
platforms.each do |platform|
  filtered_by_platform = data.select { |game| game['platform'].include?(platform) }
  platform_genres_number[platform] = Hash[genres.map { |genre| [genre, filtered_by_platform.select { |game| game['genre'].include?(genre) }.count] }]
end

puts "Total loaded games: #{games_total_number}"

result = {
  total_number: games_total_number,
  number_by_genre: number_by_genre,
  number_by_platform: number_by_platform,
  highest_scored: high_scored_games,
  number_by_years: games_per_year,
  high_reviewed_games: high_reviewed_games,
  number_by_authors: authors_games_number,
  number_per_platform_by_genre: platform_genres_number
}

File.open("result.json","w") do |f|
  f.write(JSON.pretty_generate(result))
end
