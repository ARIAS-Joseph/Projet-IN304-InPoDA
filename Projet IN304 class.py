#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import folium
from collections import Counter
from geopy.geocoders import Nominatim
import regex as re
import plotly.express as px
import pandas as pd
import os
import emoji
import gradio as gr
import operator
import threading
import plotly.graph_objects as go

avancement_map = 0
fin_map = 0
analyse_finished = 0
file_path = ''


class Tweet:
    used_hashtag = {}  # dictionnaire avec le nom du hashtag en clé et la liste des tweets contenant le hashtag en
    # valeur
    used_hashtag_sorted = []
    user_mentioned = {}  # dictionnaire avec le nom de l'utilisateur en clé et la liste des tweets mentionnant
    # l'utilisateur en valeur
    user_mentioned_sorted = []
    tweets_of_users = {}  # dictionnaire avec le nom de l'utilisateur en clé et la liste des tweets de l'utilisateur en
    # valeur
    tweets_of_users_sorted = []
    tweets_users = []
    tweets_polarity = [0, 0, 0]  # avec en indice 0 le nombre de tweets négatifs, en indice 1 le nombre de tweets
    # neutres et en indice 2 le nombre de tweets positifs
    tweets_objectivity = [0, 0]  # avec en indice 0 le nombre de tweets objectifs et en indice 1 le nombre de tweets
    # subjectifs
    topics = {}
    tweets_localization = []  # liste de toutes les localisations des tweets
    topics_sorted = []
    tweets_time = {str(i).zfill(2): 0 for i in range(24)}  # création des clés dans le dictionnaire dans l'ordre
    # croissant pour améliorer le graphique de la fonction visualize_time
    nb_tweets = 0
    compass = []
    specific_user = {}
    specific_hashtag = {}
    mentioned_by_user = {}
    hashtag_by_user = {}
    retweets = {}
    retweets_sorted = []
    languages = {}
    languages_sorted= []

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
                self.rt = int(tweet['RetweetCount'])
                self.langue = tweet['TweetLanguage']
                self.texte = tweet['TweetText']
                self.hashtag = tweet['Hashtags']
                self.mention = tweet['Mentions']
                self.polarity = tweet['Polarity']
                self.subjectivity = tweet['Subjectivity']
                self.topics = tweet['Topics']
                self.author = tweet['Author']
                Tweet.retweets[self.texte] = self.rt
                self.extract_car('#')  # extraction des hashtags utilisés dans le tweet
                self.extract_car('@')  # extraction des utilisateurs mentionnés dans le tweet
                self.analyze_sentiment()  # analyse du sentiment du tweet (négatif, neutre ou positif) et la
                # subjectivité
                self.extract_topics()  # extraction des topics du tweet
                self.list_tweet_by_author()  # ajout du tweet au dictionnaire tweets_of_users avec en clé l'auteur du
                # tweet
                self.analyse_language()
                if self.localization != "":
                    Tweet.tweets_localization.append(self.localization)
                Tweet.tweets_time[self.date[11:13]] += 1
                Tweet.nb_tweets += 1

    @staticmethod
    def instantiate_from_file(filepath="aitweets.json"):
        """ Fonction qui instancie les tweets présents dans un fichier json
        """
        global analyse_finished
        data = open(filepath, 'r', encoding='UTF-8')
        list_tweets = [js.loads(line) for line in data]

        # Noms d'utilisateurs qui seront ajoutés aux tweets afin de mieux répondre aux questions du projet étant donné
        # qu'aucun nom d'utilisateur n'est fourni (certains noms sont plus susceptibles d'apparaître souvent pour
        # rendre l'analyse des données plus intéressante)
        users_names = [*['@The_Fiend'] * 18, *['@Bray_Wyatt'] * 66, *['@Shinsuke_Nakamura'] * 11, *['@Cory'] * 20,
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

        Tweet.used_hashtag_sorted = sorted(Tweet.used_hashtag.items(),
                                           key=operator.itemgetter(1), reverse=True)  # création d'une liste
        # des hashtags présents dans les tweets analysés triée par ordre décroissant du nombre d'apparitions du
        # hashtag
        Tweet.user_mentioned_sorted = sorted(Tweet.user_mentioned.items(),
                                             key=operator.itemgetter(1),
                                             reverse=True)  # création d'une liste
        # des utilisateurs mentionnés dans les tweets analysés triée par ordre décroissant du nombre de mentions
        # de l'utilisateur
        Tweet.tweets_of_users_sorted = dict(sorted(Tweet.tweets_of_users.items(), key=lambda x: len(x[1]),
                                                   reverse=True))  # création d'une liste des utilisateurs triée
        # par ordre décroissant du nombre de tweets de l'utilisateur
        Tweet.tweets_users = [(key, len(tweets)) for key, tweets in Tweet.tweets_of_users_sorted.items()]
        Tweet.topics_sorted = sorted(Tweet.topics.items(), key=operator.itemgetter(1), reverse=True)
        Tweet.retweets_sorted = sorted(Tweet.retweets.items(), key=operator.itemgetter(1), reverse=True)
        Tweet.languages_sorted = sorted(Tweet.languages.items(), key=operator.itemgetter(1), reverse=True)
        print(Tweet.languages_sorted)

        analyse_finished = 1

    @staticmethod
    def fill_zone_atterrissage(filepath, list_tweets):
        """Remplit la zone d'atterrissage avec tous les tweets de la liste de tweets."""
        new_name = os.path.basename(filepath)
        new_name = os.path.splitext(new_name)[0]

        Tweet.reset_zone_atterrissage(new_name)
        file = open(f'zone_atterrissage_{new_name}.json', 'a')
        for tweet in list_tweets:
            tweet['TweetText'] = emoji.demojize(tweet['TweetText'])
            tweet['TweetText'] = ''.join(re.split(':[^:]+:', tweet['TweetText']))
            js.dump(tweet, file)
            file.write('\n')
        file.close()
        return f'zone_atterrissage_{new_name}.json'

    @staticmethod
    def reset_zone_atterrissage(name):
        """Supprime tout le text du fichier zone_atterrissage.txt."""
        open(f'zone_atterrissage_{name}.json', "w").close()

    def analyse_language(self):
        if self.langue == 'en':
            self.langue = 'anglais'
        elif self.langue == 'fr':
            self.langue = 'français'
        elif self.langue == 'und':
            self.langue = ''
            return
        elif self.langue == 'ja':
            self.langue = 'japonais'
        elif self.langue == 'es':
            self.langue = 'espagnol'
        elif self.langue == 'da':
            self.langue = 'danois'
        elif self.langue == 'ro':
            self.langue = 'roumain'
        elif self.langue == 'pt':
            self.langue = 'portugais'
        elif self.langue == 'ko':
            self.langue = 'coréen'
        elif self.langue == 'de':
            self.langue = 'allemand'
        elif self.langue == 'in':
            self.langue = 'maori'
        elif self.langue == 'it':
            self.langue = 'italien'
        elif self.langue == 'ar':
            self.langue = 'arabe'
        elif self.langue == 'fa':
            self.langue = 'persan'
        elif self.langue == 'ca':
            self.langue = 'catalan'
        elif self.langue == 'fi':
            self.langue = 'finnois'
        try:
            Tweet.languages[self.langue] += 1
        except KeyError:
            Tweet.languages[self.langue] = 1

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
            specific = Tweet.specific_user
            for user in name_car:
                try:
                    Tweet.mentioned_by_user[self.author].append(user)
                except KeyError:
                    Tweet.mentioned_by_user[self.author] = [user]
        elif car == "#":  # si on veut extraire les hashtags utilisés
            list_car = self.hashtag
            used_car = Tweet.used_hashtag
            name_car = re.findall(r'#\w+', txt)
            specific = Tweet.specific_hashtag
            for hashtag in name_car:
                try:
                    Tweet.hashtag_by_user[hashtag].append(self.author)
                except KeyError:
                    Tweet.hashtag_by_user[hashtag] = [self.author]
        else:
            return f'Le caractère {car} ne correspond ni aux hashtags ni aux mentions'
        for element in name_car:
            list_car.append(element)
            if element in used_car:
                used_car[element] += 1
            else:
                used_car[element] = 1
            if element in specific:
                specific[element].append(txt)
            else:
                specific[element] = [txt]

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
        Tweet.compass.append([sentiment[0], sentiment[1]])

    def extract_topics(self):
        equivalence = {'artificial intelligence': ['ai', 'artificialintelligence', 'artificial', 'artif', 'arti', 'art',
                                                   'intoainews', 'intelligence', 'artificial_intelligence',
                                                   'artificia', 'artificialin', 'artificialintellig',
                                                   'artificialintellige', 'artificialintell', 'ainews', 'artificialint',
                                                   'artificialintelli', 'artific', 'ia', 'inteligenciaartificial',
                                                   'artificialintelligen', 'artificialintel', 'artificialinte',
                                                   'arificialinterlligence', 'artificialintelligenc', 'intela',
                                                   'artificialintelligenc', 'ronald_teaches_artificial_intelligence',
                                                   'artificial intelligence', 'ia', 'artifici',
                                                   'artificialintelligencetechnology'],
                       'machine learning': ['machinelearn', 'machinelearning', 'ml', 'deeplearning', 'learning',
                                            'machine', 'dl', 'nlp', 'machinelea', 'datascien', 'machi', 'machinelearni'
                                                                                                        'deeple',
                                            'mach', 'machinelearnin', 'tensorflow', 'deepneuralnetworks',
                                            'machinele', 'neuralnetworks', 'machin', 'machinelear', 'sciketlearn',
                                            'deeplearningframework', '100daysofmlcode', 'machinelearni',
                                            'machine learning', 'deeple'],
                       'data': ['datascience', 'bigdata', 'analytics', 'data', 'datatype', 'datax', 'datas', 'datasc',
                                'bigdat', 'datasci', 'dat', 'hdatasystems'],
                       'programmation': ['python', 'python3', 'programming', '100daysofcode', 'coding', 'javascript',
                                         'java', 'sql', 'code', 'cod', '100da', '100daysof', 'pytho', '100days',
                                         'fullstack', '100day', 'coder', '100daysofcod', 'cloudcomputing', 'prog',
                                         'flutte', 'algorithm', 'programmerlife', 'iot', 'programmation', 'numpy',
                                         'devcommunity']
                       }
        for hashtag in self.hashtag:
            hashtag = hashtag[1::].lower()
            for topic in equivalence:
                if hashtag in equivalence[topic] or self.texte.lower() in equivalence[topic]:
                    hashtag = topic
            self.topics.append(hashtag)
        for topic in self.topics:
            if topic in Tweet.topics:
                Tweet.topics[topic] += 1
            else:
                Tweet.topics[topic] = 1

    def list_tweet_by_author(self):
        """Fonction qui ajoute le tweet à la liste des tweets d'un utilisateur
        """
        try:
            Tweet.tweets_of_users[self.author].append(self.texte)
        except KeyError:
            Tweet.tweets_of_users[self.author] = [self.texte]


def user_mention_specific_hashtag(hashtag: str):
    if hashtag[0] != '#':
        hashtag = '#' + hashtag
    try:
        i = 1
        for utilisateur in Tweet.hashtag_by_user[hashtag]:
            print(f'Utilisateur n°{i} utilisant {hashtag}: {utilisateur}')
            i += 1
    except KeyError:
        print(f'{hashtag} n\'a jamais été utilisé')


def users_mention_by_user(user: str):
    if user[0] != '@':
        user = '@' + user
    try:
        i = 1
        for utilisateur in Tweet.mentioned_by_user[user]:
            print(f'Utilisateur n°{i} mentionné par {user}: {utilisateur}')
            i += 1
    except KeyError:
        print(f'{user} n\'a jamais mentionné ou tweeté')


def get_top(list_used=Tweet.used_hashtag_sorted, k=10):
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
        try:
            if list_used == Tweet.tweets_users:
                top = 'utilisateur'
                mention = 'tweet'
                x_label = 'Utilisateurs'
                y_label = 'Nombre de tweets'
            elif list_used == Tweet.used_hashtag_sorted:
                top = 'hashtag'
                mention = 'occurrence'
                x_label = 'Hashtags'
                y_label = 'Nombre d\'utilisations'
            elif list_used == Tweet.user_mentioned_sorted:
                top = 'utilisateur mentionné'
                mention = 'mention'
                x_label = 'Utilisateurs mentionnés'
                y_label = 'Nombre de mentions'
            elif list_used == Tweet.topics_sorted:
                top = 'sujets de discussions'
                mention = 'mention'
                x_label = 'topics mentionnés'
                y_label = 'Nombre de mentions'
            else:
                return f'La liste {list_used} n\'est pas compatible avec la fonction top'

            print(
                f"Top {i + 1} {top} : {list_used[i][0]} avec {list_used[i][1]} {mention}"
                f"{'s' if list_used[i][1] > 1 else ''}")
            name.append(list_used[i][0])
            occurrence.append(list_used[i][1])
        except IndexError:
            pass
    df = pd.DataFrame({x_label: name, y_label: occurrence})
    fig = px.bar(df, x=x_label, y=y_label, text=y_label, title=f'Top {k} des {top}s',
                 labels={x_label: x_label, y_label: y_label})
    return fig


def top_retweets(k):
    for i in range(0, k):
        print(
            f"Top {i + 1} des tweets les plus retweetés :\n\"{Tweet.retweets_sorted[i][0]}\"\n avec "
            f"{Tweet.retweets_sorted[i][1]} retweet{'s' if Tweet.retweets_sorted[i][1] > 1 else ''}\n")


def mention_specific(list_used: dict, mention: str):
    if list_used == Tweet.specific_user:
        i = 1
        try:
            for tweet in list_used[mention]:
                print(f'Tweet n°{i} mentionnant {mention}:\n{tweet}')
                i += 1
        except KeyError:
            print('Cet utilisateur n\'a jamais été mentionné')
    elif list_used == Tweet.specific_hashtag:
        i = 1
        try:
            for tweet in list_used[mention]:
                print(f'Tweet n°{i} utilisant {mention}:\n{tweet}')
                i += 1
        except KeyError:
            print('Ce hashtag n\'a jamais été utilisé')


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
        i = 1
        for tweet in Tweet.tweets_of_users[author]:
            print(f'Tweet {i}:\n{tweet}\n')
            i += 1
    except KeyError:
        print('Cet utilisateur n\'a pas tweeté ou n\'existe pas')


def number_publication(author: str):
    if author[0] != '@':
        author = '@' + author
    try:
        print(f'{author} a tweeté {len(Tweet.tweets_of_users[author])} fois')
    except KeyError:
        print('Cet utilisateur n\'a pas tweeté ou n\'existe pas')


def languages_plot(k):
    top_k_languages = Tweet.languages_sorted[:k]  # Sélectionner les k premières langues

    # Extraire les noms des langues et les compteurs
    languages = [lang[0] for lang in top_k_languages]
    counts = [lang[1] for lang in top_k_languages]

    # Créer le graphique pie chart avec Plotly Express
    fig = px.pie(names=languages, values=counts, title=f'Top {k} des langues les plus utilisées')
    fig.show()


def show_pie_chart(list_used: list):
    if list_used == Tweet.tweets_polarity:
        labels = 'Négatif', 'Neutre', 'Positif'
        sizes = Tweet.tweets_polarity
        colors = ['silver', 'lightcoral', 'cornflowerblue']
        title = 'Représentation de la polarité des tweets'
    elif list_used == Tweet.tweets_objectivity:
        labels = 'Objectif', 'Subjectif'
        sizes = Tweet.tweets_objectivity
        colors = ['cornflowerblue', 'lightcoral']
        title = 'Représentation de l\'objectivité des tweets'
    else:
        return f'La liste {list_used} n\'est pas compatible avec la fonction show_pie_chart'
    df = pd.DataFrame({'labels': labels, 'sizes': sizes})
    fig = px.pie(df, names='labels', values='sizes', title=title, color_discrete_sequence=colors)
    fig.show()


def show_pie_chart2():
    df = pd.DataFrame(Tweet.compass, columns=['Polarité', 'Subjectivité'])
    fig = px.scatter(df, x='Subjectivité', y='Polarité',
                     color='Polarité', color_continuous_scale='RdBu',
                     title='Visualisation des Tweets selon la Subjectivité et la Polarité')
    # Centrage du graphique
    fig.update_layout(xaxis=dict(range=[-0.1, 1.1], zeroline=False, showline=False),
                      yaxis=dict(range=[-1.1, 1.1], zeroline=True, zerolinewidth=1, zerolinecolor='black'),
                      plot_bgcolor='darkseagreen', margin=dict(l=0, r=0, t=0, b=0))

    # Ajout d'une ligne verticale à 0.5 sur l'axe de la subjectivité
    fig.add_shape(type='line', x0=0.5, y0=-1.1, x1=0.5, y1=1.1, line=dict(color='black', width=1))

    # Mise en forme du graphique
    fig.update_traces(marker=dict(size=12, opacity=0.8), selector=dict(mode='markers+text'))
    fig.update_layout(xaxis_title='Subjectivité', yaxis_title='Polarité')
    fig.update_coloraxes(colorbar_title='Polarité')

    # Réglage de l'axe x pour placer la ligne zéro à 0.5 et cacher les valeurs dépassant les seuils
    fig.update_xaxes(showgrid=False, tickvals=[0, 0.5, 1], ticktext=['0', '0.5', '1'], tickmode='array')
    fig.update_yaxes(showgrid=False, tickvals=[-1, 0, 1], ticktext=['-1', '0', '1'], tickmode='array')

    return fig


def world_map(start=0, end=0, user='Géolocalisation_tweet'):
    print('World Map')
    global fin_map
    global avancement_map
    global analyse_finished
    while analyse_finished != 1:
        time.sleep(1)
    if end == 0:
        end = len(Tweet.tweets_localization)
    debut = time.time()
    geolocator = Nominatim(user_agent=user)
    tweet_coordinates = {}
    avancement_map = 1
    for location in Tweet.tweets_localization[start:end]:
        try:
            location = location.strip()
            if location not in tweet_coordinates:
                location_data = geolocator.geocode(location)
                if location_data:
                    tweet_coordinates[location] = (location_data.latitude, location_data.longitude, location)
            if avancement_map % 10 == 0 or avancement_map == 1:
                print(avancement_map, '/', len(Tweet.tweets_localization))
            avancement_map += 1
        except ConnectionError:
            print(f'Une erreur de connection est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}')
            avancement_map += 1
        except TimeoutError:
            print(f'Une erreur de type Timeout est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}')
            avancement_map += 1
        except geopy.exc.GeocoderUnavailable:
            print(f'Une erreur est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}. Soit la connexion n\'a pas pu être établis avec le service de géolocalisation'
                  f' soit le service n\'est pas disponible')
        except geopy.exc.GeocoderQuotaExceeded:
            print(f'Une erreur est survenue lors de la création de la carte avec la localisation suivante: {location}'
                  f'à cause d\'un trop grand nombre de requête en un certain laps de temps.')
        except Exception as error:
            print(f'Une erreur de type {type(error)}est survenue lors de la création de la carte avec la localisation '
                  f'suivante: {location}')
            avancement_map += 1

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
    print('temps final:', fin - debut)
    fin_map = 1


def visualize_tweet_time():
    time = list(Tweet.tweets_time.keys())
    nb_tweets = list(Tweet.tweets_time.values())
    df = pd.DataFrame({'Heure': time, 'Nombre de Tweets': nb_tweets})
    plot_time = px.line(df, x='Heure', y='Nombre de Tweets', markers=True, line_shape='linear',
                        labels={'Heure': 'Heure', 'Nombre de Tweets': 'Nombre de Tweets'},
                        title='Nombre de Tweets par Heure')
    return plot_time


def start():
    global file_path
    """print(file)
    interface_init.close()
    interface.launch()"""
    Tweet.instantiate_from_file()
    return {
        welcome_label: gr.Label(visible=False),
        analyze_button: gr.Button(visible=False),
        upload_file_button: gr.UploadButton(visible=False),
        analysis: gr.Radio(visible=True)
    }


def change_r(choice: str):
    if choice == Radio_Choices[-1]:
        return {plot: gr.Plot(visible=False),
                top: gr.Dropdown(visible=False),
                others: gr.Dropdown(visible=False)}

    if choice == Radio_Choices[0]:
        return {top: gr.Dropdown(visible=True),
                others: gr.Dropdown(visible=False),
                plot: gr.Plot(visible=False)}

    if choice == Radio_Choices[1]:
        return {others: gr.Dropdown(visible=True),
                top: gr.Dropdown(visible=False),
                plot: gr.Plot(visible=False)}


def change_top(choice: str):
    if choice == "Top hashtags":
        return {plot: gr.Plot(value=get_top(list_used=Tweet.used_hashtag_sorted, k=10), visible=True)}
    if choice == "Top utilisateurs":
        return {plot: gr.Plot(value=get_top(list_used=Tweet.tweets_users, k=10), visible=True)}
    if choice == "Top utilisateurs mentionnés":
        return {plot: gr.Plot(value=get_top(list_used=Tweet.user_mentioned_sorted, k=10), visible=True)}
    if choice == "Top topics":
        return {plot: gr.Plot(value=get_top(list_used=Tweet.topics_sorted, k=10), visible=True)}


"""def change_act(choice: str):
    if choice == "Nombre de publications par utilisateur":
        return {publi_user: gr.Textbox(value=number_publication("@Martin"), visible=True)}
    if choice == "Tous les Tweets d'un utilisateur":
        pass
        # return {plot  : gr.Plot(visible=True)} #ajouter value
    if choice == "Tous les utilisateurs mentionnés par un utilisateur":
        pass
        # return {plot  : gr.Plot(visible=True)} #ajouter value


def change_publi(choice: str):
    if choice == "Nombre de publications par topic":
        return {topic: gr.Textbox(visible=True)}
        # return {plot  : gr.Plot(visible=True)} #ajouter value
    if choice == "Nombre de publications par hashtag":
        return {hashtag: gr.Textbox(visible=True)}
        # return {plot  : gr.Plot(visible=True)} #ajouter value
    if choice == "Tous les utilisateurs d'un hashtag":
        return {hashtag: gr.Textbox(visible=True)}
        # return {plot  : gr.Plot(visible=True)} #ajouter value"""


def change_others(choice: str):
    if choice == "Heures de Tweet":
        return {plot: gr.Plot(value=visualize_tweet_time(), visible=True)}
    if choice == "Polarité/Subjectivité":
        return {plot: gr.Plot(value=show_pie_chart2(), visible=True)}
    if choice == "Répartition mondiale":
        return {carte: gr.HTML(value='tweet_map.html', visible=True)}


"""def change_slider(value: int):
    val = value if value != 0 else 10
    return {plot: gr.Plot(value=get_top(k=value), visible=True),
            slider: gr.Slider(1, 50, val, step=1, label="Les Top combien voulez-vous voir ?",
                              info="Déplacez le curseur", visible=True, interactive=True)}"""


def upload_file(file):
    global file_path
    file_path = file
    start()


Radio_Choices = ["Top (4)",
                 "Caractéristiques (3)",
                 "Masquer"]

with gr.Blocks(theme=gr.themes.Soft(neutral_hue='cyan')) as interface:
    title = gr.Label(label="InPoDa", value="InPoDa", color="#00ACEE")
    welcome_label = gr.Label(label="Bonjour", value="Bienvenue sur InPoDa, la plateforme d'analyse de données de"
                                                    "réseaux sociaux.\nVeuillez choisir un fichier à analyser")
    # file_output = gr.File()
    upload_file_button = gr.UploadButton("Cliquez pour choisir le fichier à analyser",
                                         file_types=[".json"], file_count="single", visible=False)
    analyze_button = gr.Button(value="Lancer l'analyse", visible=True)
    carte = gr.HTML(visible=False)
    analysis = gr.Radio(choices=Radio_Choices,
                        value="Masquer",
                        label="Analyses",
                        info="Que voulez-vous analyser ?",
                        visible=False,
                        interactive=True)
    top = gr.Dropdown(choices=["Top hashtags", "Top utilisateurs", "Top utilisateurs mentionnés", "Top topics"],
                      label="Top", info="Veuillez sélectionner l'élément dont vous voulez voir le Top :", visible=False)
    """act = gr.Dropdown(choices=["Nombre de publications par utilisateur", "Tous les Tweets d'un utilisateur",
                               "Tous les utilisateurs mentionnés par un utilisateur"],
                      label="Activité", info="Veuillez sélectionner l'activité que vous souhaitez observer :",
                      visible=False)
    publi = gr.Dropdown(choices=["Nombre de publications par topic", "Nombre de publications par hashtag",
                                 "Tous les utilisateurs d'un hashtag"],
                        label="Catégories", info="Veuillez sélectionner les publications que vous voulez analyser :",
                        visible=False)"""
    others = gr.Dropdown(choices=["Heures de Tweet", "Polarité/Subjectivité", "Répartition mondiale"],
                         label="Autres", info="Veuillez sélectionner ce que vous souhaitez analyser :", visible=False)

    hashtag = gr.Textbox(info="Rentrez le hashtag", visible=False, interactive=True)
    topic = gr.Textbox(info="Rentrez le topic :", visible=False, interactive=True)
    plot = gr.Plot(visible=False)
    slider = gr.Slider(visible=False)
    publi_user = gr.Textbox(info="Quel utilisateur ?", visible=False)
    # slider.change(change_r,inputs=[analysis,slider],outputs=plot)
    analysis.change(change_r, inputs=[analysis], outputs=[top, others, plot])
    top.change(change_top, inputs=[top], outputs=[plot])
    """act.change(change_act, inputs=[act], outputs=[publi_user])
    publi.change(change_publi, inputs=[publi], outputs=[hashtag, topic])"""
    others.change(change_others, inputs=[others], outputs=[plot])
    """hashtag.change(change_hashtag, inputs=[hashtag], outputs=[plot])
    topic.change(change_topic, inputs=[topic], outputs=[plot])"""
    interface.load(change_r, inputs=[analysis], outputs=[plot])
    analyze_button.click(start, outputs=[welcome_label, upload_file_button, analyze_button, analysis])
    upload_file_button.click(upload_file, outputs=[welcome_label, upload_file_button, analyze_button, analysis])


if __name__ == '__main__':
    Tweet.instantiate_from_file('aitweets.json')
    thread_map = threading.Thread(target=world_map)
    thread_map.start()

    # Partie qui permettrait d'accélérer le processus de world map mais qui est impossible, car geopy refuse un trop
    # grand nombre de requêtes en un certain laps de temps. Pour régler ce problème, on pourrait essayer de passer par
    # un API nœud de TOR avant de changer les ip

    """thread_map = []
    for i in range(0, len(Tweet.tweets_localization), 100):
        print('création du thread', i % 100)
        end = min(i + 100,
                  len(Tweet.tweets_localization))
        t = threading.Thread(target=world_map, args=(i, end, get_password(10)))
        thread_map.append(t)
        t.start()
        time.sleep(random.randint(1,5))"""

    interface.launch()
