__author__ = "Mathilde GAUTEUR, Joseph ARIAS"
__copyright__ = "Copyright 2023, Projet InPoDa"
__credits__ = ["Mathilde GAUTEUR", "Joseph ARIAS"]
__license__ = "GPL"
__maintainer__ = "Joseph ARIAS"
__email__ = "joseph.arias@ens.uvsq.fr"
__status__ = "Development"

import json as js
import time

import geopy.exc
from textblob import TextBlob
import random
import matplotlib.pyplot as plt
import folium
from collections import Counter
from geopy.geocoders import Nominatim
import regex as re
import plotly
import plotly.graph_objs as go
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import emoji
import os


class Tweet:
    used_hashtag = {}  # dictionnaire avec le nom du hashtag en clé et la liste des tweets contenant le hashtag en
    # valeur
    user_mentioned = {}  # dictionnaire avec le nom de l'utilisateur en clé et la liste des tweets mentionnant
    # l'utilisateur en valeur
    tweets_of_users = {}  # dictionnaire avec le nom de l'utilisateur en clé et la liste des tweets de l'utilisateur en
    # valeur
    tweets_polarity = [0, 0, 0]  # avec en indice 0 le nombre de tweets négatifs, en indice 1 le nombre de tweets
    # neutres et en indice 2 le nombre de tweets positifs
    tweets_objectivity = [0, 0]  # avec en indice 0 le nombre de tweets objectifs et en indice 1 le nombre de tweets
    # subjectifs
    tweets_localization = []  # liste de toutes les localisations des tweets
    tweets_time = {str(i).zfill(2): 0 for i in range(24)}  # création des clés dans le dictionnaire dans l'ordre
    # croissant pour améliorer le graphique de la fonction visualize_time
    all_tweets = []  # liste de tous les tweets

    def __init__(self, tweet: dict):

        if not isinstance(tweet, dict):
            print(f'Un élément n\'est pas un dictionnaire et n\'a donc pas pu être analysé: {tweet}')
        else:
            required_keys = ['id', 'AuthorLocation', 'CreatedAt', 'RetweetCount', 'TweetLanguage', 'TweetText']
            missing_keys = [key for key in required_keys if key not in tweet]
            if missing_keys:
                print(f"Attention : Le dictionnaire {tweet} ne contient pas toutes les clés requises ! \n"
                      f"Clé{'s' if len(missing_keys) > 1 else ''} manquante{'s' if len(missing_keys) > 1 else ''} : "
                      f"{', '.join(missing_keys)}")
            else:
                tweet['Hashtags'] = []
                tweet['Mentions'] = []
                tweet['Topics'] = []
                tweet['Polarity'] = ''
                tweet['Subjectivity'] = ''
                self.id = tweet['id']
                self.localization = tweet['AuthorLocation']
                self.date = tweet['CreatedAt']
                self.rt = tweet['RetweetCount']
                self.langue = tweet['TweetLanguage']
                self.texte = tweet['TweetText']
                self.hashtag = tweet['Hashtags']
                self.mention = tweet['Mentions']
                self.polarity = tweet['Polarity']
                self.subjectivity = tweet['Subjectivity']
                self.topics = tweet['Topics']
                self.author = tweet['Author']
                self.extract_car('#')  # extraction des hashtags utilisés dans le tweet
                self.extract_car('@')  # extraction des utilisateurs mentionnés dans le tweet
                self.analyze_sentiment()  # analyse du sentiment du tweet (négatif, neutre ou positif) et la
                # subjectivité
                self.extract_topics()  # extraction des topics du tweet
                self.list_tweet_by_author()  # ajout du tweet au dictionnaire tweets_of_users avec en clé l'auteur du
                # tweet
                Tweet.used_hashtag_sorted = sorted(Tweet.used_hashtag.items(),
                                                 key=lambda item: len(item[1]), reverse=True)  # création d'une liste
                # des hashtags présents dans les tweets analysés triée par ordre décroissant du nombre d'apparitions du
                # hashtag
                Tweet.user_mentioned_sorted = sorted(Tweet.user_mentioned.items(),
                                                   key=lambda item: len(item[1]), reverse=True)  # création d'une liste
                # des utilisateurs mentionnés dans les tweets analysés triée par ordre décroissant du nombre de mentions
                # de l'utilisateur
                Tweet.tweets_of_users_sorted = sorted(Tweet.tweets_of_users.items(),
                                                    key=lambda item: len(item[1]), reverse=True)  # création d'une liste
                # des utilisateurs triée par ordre décroissant du nombre de tweets de l'utilisateur
                if self.localization != "":
                    Tweet.tweets_localization.append(self.localization)
                if self.date[11:13] in Tweet.tweets_time:
                    Tweet.tweets_time[self.date[11:13]] += 1
                else:
                    Tweet.tweets_time[self.date[11:13]] = 1
                Tweet.all_tweets.append(self)

    @classmethod
    def instantiate_from_file(cls, test=0):
        """ Fonction qui instancie les tweets présents dans un fichier json
        """

        filepath = filedialog.askopenfilename(title='Ouvrir un fichier json')
        error = 0
        while not filepath.endswith(".json") and filepath != '':
            filepath = filedialog.askopenfilename(title=f'OUVRIR UN FICHIER JSON{' !' * error}')
            error += 1

        data = open(filepath, 'r', encoding='UTF-8')
        list_tweets = [js.loads(line) for line in data]

        # Noms d'utilisateurs qui seront ajoutés aux tweets afin de mieux répondre aux questions du projet étant donné
        # qu'aucun nom d'utilisateur n'est fourni (certains noms sont plus susceptibles d'apparaître souvent afin de
        # rendre l'analyse des données plus intéressante)
        users_names = [*['@The Fiend'] * 18, *['@Bray Wyatt'] * 66, *['@Shinsuke Nakamura'] * 11, *['@Cory'] * 20,
                    '@Chumlee', '@Liklenb', '@Jean_Valjean', '@Martin', '@Dupont', *['@IainLJBrown'] * 100,
                    *['@Paula_Piccard'] * 50, *['@nigewillson'] * 25, *['@machinelearnTec'] * 15, '@Karl_Marx',
                    *['@akbarth3great'] * 15, '@JoshuaBarbeau', '@sankrant', '@machinelearnflx', '@SpirosMargaris',
                    *['@Datascience__'] * 30, *['@Charles_Henry'] * 38, *['@UEYvelines'] * 78,
                    *['@unionetudiante_'] * 99, *['@la_classe_ouvriere'] * 16, *['@ogcnice'] * 6, '@Utah',
                    '@chachat']

        for i in range(len(list_tweets)):
            list_tweets[i]['Author'] = random.choice(users_names)

        file = Tweet.fill_zone_atterrissage(filepath, list_tweets)
        data = open(file, 'r', encoding='UTF-8')
        list_tweets = [js.loads(line) for line in data]
        for tweet in list_tweets:
            Tweet(tweet)

        data.close()

        button_file.destroy()
        label_file.destroy()

        button_analyze = tk.Button(text='Analyser')
        button_analyze.grid()

    @staticmethod
    def fill_zone_atterrissage(filepath, list_tweets):
        """Remplit la zone d'atterrissage avec tous les objets tweets de la liste de tweets."""
        new_name = os.path.basename(filepath)
        new_name = os.path.splitext(new_name)[0]

        Tweet.reset_zone_atterrissage(new_name)
        file = open(f'zone_atterrissage_{new_name}.json', 'a')
        for tweet in list_tweets:
            tweet['TweetText'] = emoji.demojize(tweet['TweetText'])  # on supprime les emojis du tweet
            js.dump(tweet, file)
            file.write('\n')
        file.close()
        return f'zone_atterrissage_{new_name}.json'

    @staticmethod
    def reset_zone_atterrissage(name):
        """Supprime tout le text du fichier zone_atterissage.txt."""
        open(f'zone_atterrissage_{name}.json', "w").close()

    def extract_car(self, car: str):
        """Fonction qui extrait les hashtags utilisés ou les utilisateurs mentionnés dans le tweet à partir d'une base
        de données et les ajoute à la base de données

        Parameters
        ----------
        car : str
            Le caractère que l'on recherche (# si on cherche les hashtags et @ si on cherche les utilisateurs"
        """

        txt = self.texte
        if car == "@":  # si on veut extraire les utilisateurs mentionnés
            list_car = self.mention
            used_car = Tweet.user_mentioned
            name_car = re.findall(r'@\w+', txt)
        elif car == "#":  # si on veut extraire les hashtags utilisés
            list_car = self.hashtag
            used_car = Tweet.used_hashtag
            name_car = re.findall(r'#\w+', txt)
        else:
            return f'Le caractère {car} ne correspond ni aux hashtags ni aux mentions'
        for element in name_car:
            list_car.append(element)
            if element in used_car:
                used_car[element].append(self)
            else:
                used_car[element] = [self]

    def analyze_sentiment(self):
        """Fonction qui analyse le sentiment d'un tweet (négatif, neutre ou positif)
        """
        sentiment = TextBlob(self.texte).sentiment
        if sentiment[0] < 0:
            self.polarity = 'Negative'
            Tweet.tweets_polarity[0] += 1
        elif sentiment[0] == 0:
            self.polarity = 'Neutral'
            Tweet.tweets_polarity[1] += 1
        elif sentiment[0] > 0:
            self.polarity = 'Positive'
            Tweet.tweets_polarity[2] += 1

        if sentiment[1] <= 0.5:
            self.subjectivity = 'Objective'
            Tweet.tweets_objectivity[0] += 1
        elif sentiment[1] >= 0.5:
            self.subjectivity = 'Subjectif'
            Tweet.tweets_objectivity[1] += 1

    def extract_topics(self):
        pass

    def list_tweet_by_author(self):
        """Fonction qui ajoute le tweet à la liste des tweets d'un utilisateur
        """
        try:
            Tweet.tweets_of_users[self.author].append(self)
        except KeyError:
            Tweet.tweets_of_users[self.author] = [self]


def top(list_used: list, k: int):
    """Top k hashtags ou Top k utilisateurs mentionnés

    Fonction qui affiche les top k hashtags ou les tops k utilisateurs mentionnés

    Paramètres
    ----------
    list_used : list
        liste des hashtags et leurs occurrences ou liste des mentions d'utilisateurs et leurs occurrences
    k : int
        les k hashtags ou utilisateurs qui reviennent le plus

    """
    name = []
    occurrence = []
    for i in range(0, k):
        if list_used == Tweet.tweets_of_users_sorted:
            top = 'utilisateur'
            mention = 'tweet'
            xlabel = 'Utilisateurs'
            ylabel = 'Nombre de tweets'
        elif list_used[i][0][0] == '#':
            top = 'hashtag'
            mention = 'occurrence'
            xlabel = 'Hashtags'
            ylabel = 'Nombre d\'utilisations'
        elif list_used[i][0][0] == '@':
            top = 'utilisateur mentionné'
            mention = 'mention'
            xlabel = 'Utilisateurs mentionnés'
            ylabel = 'Nombre de mentions'
        else:
            return f'La liste {list_used} n\'est pas compatible avec la fonction top'
        print(
            f"Top {i + 1} {top} : {list_used[i][0]} avec {len(list_used[i][1])} {mention}"
            f"{'s' if len(list_used[i][1]) > 1 else ''}")
        name.append(list_used[i][0])
        occurrence.append(len(list_used[i][1]))

    ax = plt.bar(name, occurrence)
    for bar in ax:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.0f}', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'Top {k} des {top}s')
    plt.show()


def number_hashtag(hashtag: str):
    """Nombre de publications par hashtag

    Fonction qui affiche le nombre de publications pour un hashtag donné

    Paramètres
    ----------
    hashtag : str
        nom du hashtag que l'on veut compter

    """
    if hashtag[0] != '#':
        hashtag = '#' + hashtag
    dic_hashtag = Tweet.used_hashtag[hashtag]
    print(f"Le hashtag {hashtag} apparaît dans {len(dic_hashtag)} publication"
          f"{'s' if len(dic_hashtag) > 1 else ''}")


def publication_author(author: str):
    """Tweets de l'auteur
    Fonction qui affiche les tweets d'un utilisateur donné

    Paramètres
    ----------
    author : str
        nom de l'auteur dont on veut les tweets

    """
    if author[0] != '@':
        author = '@' + author
    try:
        for tweet in Tweet.tweets_of_users[author]:
            print(tweet.texte)
    except KeyError:
        print('Cet utilisateur n\'a pas tweeté')


def show_pie_chart(list_used: list):
    if list_used == Tweet.tweets_polarity:
        labels = 'Négatif', 'Neutre', 'Positif'
        sizes = Tweet.tweets_polarity
        colors = ['lightcoral', 'silver', 'cornflowerblue']
        title = 'Représentation de la polarité des tweets'
    elif list_used == Tweet.tweets_objectivity:
        labels = 'Objectif', 'Subjectif'
        sizes = Tweet.tweets_objectivity
        colors = ['lightcoral', 'cornflowerblue']
        title = 'Représentation de l\'objectivité des tweets'
    else:
        return f'La liste {list_used} n\'est pas compatible avec la fonction show_pie_chart'

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title(title)
    plt.show()


def world_map():
    debut = time.time()
    geolocator = Nominatim(user_agent="Géolocalisation_tweets")
    tweet_coordinates = {}
    i = 1
    for location in Tweet.tweets_localization:
        try:
            location = location.strip()
            if location not in tweet_coordinates:
                location_data = geolocator.geocode(location)
                if location_data:
                    tweet_coordinates[location] = (location_data.latitude, location_data.longitude, location)
            if i % 10 == 0 or i == 1:
                print(i, '/', len(Tweet.tweets_localization))
            i += 1
        except ConnectionError:
            print(f'Une erreur de connection est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}')
            i += 1
        except TimeoutError:
            print(f'Une erreur de type Timeout est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}')
            i += 1
        except geopy.exc.GeocoderUnavailable:
            print(f'Une erreur est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}. Soit la connexion n\'a pas pu être établis avec le service de géolocalisation'
                  f' soit le service n\'est pas disponible')
        except Exception as error:
            print(f'Une erreur de type {type(error)}est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}')
            i += 1

    tweet_counts = Counter(Tweet.tweets_localization)
    m = folium.Map()

    for location, count in tweet_counts.items():
        if location in tweet_coordinates:
            lat, lon = tweet_coordinates[location][:2]
            popup_content = f'<p><b>{tweet_coordinates[location][2]}</b></p>' \
                            f'<p>{count} tweet{"s" if count > 1 else ""}' \
                            f' posté{"s" if count > 1 else ""} depuis cet endroit</p>'  # utilisation de html qui
            # est nécessaire étant donné que le fichier contenant la carte est en html
            popup = folium.Popup(popup_content, parse_html=False, max_width=100)
            """icon_image = "icone_twitter.png"
            coeff = 1 + count*0.05
            icon = folium.CustomIcon(
                icon_image,
                icon_size=(50*coeff, 50*coeff),
                icon_anchor=(0, 0),
                popup_anchor=(0, 0)
            )"""
            folium.Marker(location=(lat, lon), popup=popup).add_to(m)

    m.save('tweet_map.html')
    fin = time.time()
    print('temps final:', fin-debut)


def visualize_tweet_time():
    time = list(Tweet.tweets_time.keys())
    nb_tweets = list(Tweet.tweets_time.values())

    plt.figure(figsize=(10, 6))
    plt.plot(time, nb_tweets, color='skyblue', marker='o', linewidth=3, markeredgewidth=10)
    plt.xlabel('Heure')
    plt.ylabel('Nombre de Tweets')
    plt.title('Nombre de Tweets par Heure')
    plt.xticks(time)
    plt.yticks(range(min(nb_tweets)-1, max(nb_tweets) + 1, 2))
    plt.grid(True)
    plt.tight_layout()
    plt.show()


window = tk.Tk()
window.title('InPoDa')
path = "logo_twitter.png"
load = Image.open(path)
render = ImageTk.PhotoImage(load)
window.iconphoto(False, render)
label_file = tk.Label(window, text='Choisir un fichier contenant des tweets au format json', font=('helvetica', '20'),
                      fg='#00acee')
button_file = tk.Button(window, text='Choisir le fichier', command=Tweet.instantiate_from_file)
label_file.grid()
button_file.grid()
window.mainloop()

print(f"Nombre de tweets analysés: {len(Tweet.all_tweets) + 1}")
print(top(Tweet.user_mentioned_sorted, 15))
print(top(Tweet.used_hashtag_sorted, 15))
print(top(Tweet.tweets_of_users_sorted, 15))
print(number_hashtag("#AI"))
print(publication_author('Chumlee'))
show_pie_chart(Tweet.tweets_polarity)
show_pie_chart(Tweet.tweets_objectivity)
world_map() # cette fonction demande beaucoup de temps pour s'exécuter et dépend de la connexion internet ! La
# console affiche l'avancement de cette dernière"""

visualize_tweet_time()

