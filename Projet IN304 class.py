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
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pandas as pd
from tkinter import filedialog
import os
import emoji
import plotly.io as pio
import gradio as gr
import operator
import asyncio
import threading
import concurrent.futures


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
                                                   key=operator.itemgetter(1), reverse=True)  # création d'une liste
                # des hashtags présents dans les tweets analysés triée par ordre décroissant du nombre d'apparitions du
                # hashtag
                Tweet.user_mentioned_sorted = sorted(Tweet.user_mentioned.items(),
                                                     key=operator.itemgetter(1),
                                                     reverse=True)  # création d'une liste
                # des utilisateurs mentionnés dans les tweets analysés triée par ordre décroissant du nombre de mentions
                # de l'utilisateur
                Tweet.tweets_of_users_sorted = sorted(Tweet.tweets_of_users.items(),
                                                      key=operator.itemgetter(1),
                                                      reverse=True)  # création d'une liste des utilisateurs triée par
                # ordre décroissant du nombre de tweets de l'utilisateur
                Tweet.topics_sorted = sorted(Tweet.topics.items(), key=operator.itemgetter(1), reverse=True)
                if self.localization != "":
                    Tweet.tweets_localization.append(self.localization)
                Tweet.tweets_time[self.date[11:13]] += 1
                Tweet.nb_tweets += 1

    @staticmethod
    def instantiate_from_file(filepath="aitweets.json"):
        """ Fonction qui instancie les tweets présents dans un fichier json
        """

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
                used_car[element] += 1
            else:
                used_car[element] = 1

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
            Tweet.tweets_of_users[self.author] += 1
        except KeyError:
            Tweet.tweets_of_users[self.author] = 1


def get_top(list_used=Tweet.tweets_of_users_sorted, k=10):
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
            if list_used == Tweet.tweets_of_users_sorted:
                top = 'utilisateur'
                mention = 'tweet'
                xlabel = 'Utilisateurs'
                ylabel = 'Nombre de tweets'
            elif list_used == Tweet.used_hashtag_sorted:
                top = 'hashtag'
                mention = 'occurrence'
                xlabel = 'Hashtags'
                ylabel = 'Nombre d\'utilisations'
            elif list_used == Tweet.user_mentioned_sorted:
                top = 'utilisateur mentionné'
                mention = 'mention'
                xlabel = 'Utilisateurs mentionnés'
                ylabel = 'Nombre de mentions'
            elif list_used == Tweet.topics_sorted:
                top = 'sujets de discussions'
                mention = 'mention'
                xlabel = 'topics mentionnés'
                ylabel = 'Nombre de mentions'
            else:
                return f'La liste {list_used} n\'est pas compatible avec la fonction top'

            print(
                f"Top {i + 1} {top} : {list_used[i][0]} avec {list_used[i][1]} {mention}"
                f"{'s' if list_used[i][1] > 1 else ''}")
            name.append(list_used[i][0])
            occurrence.append(list_used[i][1])
        except IndexError:
            pass
    df = pd.DataFrame({xlabel: name, ylabel: occurrence})
    fig = px.bar(df, x=xlabel, y=ylabel, text=ylabel, title=f'Top {k} des {top}s',
                 labels={xlabel: xlabel, ylabel: ylabel})
    return fig


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
    print('temps final:', fin - debut)


def visualize_tweet_time():
    time = list(Tweet.tweets_time.keys())
    nb_tweets = list(Tweet.tweets_time.values())
    df = pd.DataFrame({'Heure': time, 'Nombre de Tweets': nb_tweets})
    plot_time = px.line(df, x='Heure', y='Nombre de Tweets', markers=True, line_shape='linear',
                        labels={'Heure': 'Heure', 'Nombre de Tweets': 'Nombre de Tweets'},
                        title='Nombre de Tweets par Heure')
    return plot_time


def start():
    """print(file)
    interface_init.close()
    interface.launch()"""
    Tweet.instantiate_from_file()
    return {
        welcome_label: gr.Label(visible=False),
        analyze_button: gr.Button(visible=False),
        analyze_file: gr.File(visible=False),
        analysis: gr.Radio(visible=True)
    }


def change_r(choice: str):
    if choice == Radio_Choices[0]:
        return {plot : gr.Plot(visible = False)}
    if choice == Radio_Choices[1]:
        change_slider()
    if choice == Radio_Choices[2]:
        return {plot: gr.Plot(value=visualize_tweet_time(), visible=True)}
    if choice == Radio_Choices[3]:
        return {plot: gr.Plot(value=show_pie_chart2(), visible=True)}
    
def change_slider(value:int):
    val = value if value != 0 else 10 
    return {plot: gr.Plot(value=get_top(k=value), visible=True), 
    slider : gr.Slider(1,50,val, step=1,label="Les Top combien voulez-vous voir ?", info="Déplacez le curseur", visible=True, interactive=True)}

"""print(Tweet.topics_sorted)
print(get_top(Tweet.topics_sorted, 10))
print(get_top(Tweet.tweets_of_users_sorted, 15))"""

Radio_Choices = ["Masquer", "Top", "Heures", "Polarité/Subjectivité", "Nb utilisation d'un #",
                 "Tweets d'un utilisateur"]

with gr.Blocks(theme=gr.themes.Soft(neutral_hue='cyan')) as interface:
    title = gr.Label(label="InPoDa", value="InPoDa", color="#00ACEE")
    welcome_label = gr.Label(label="Bonjour", value="Bienvenue sur InPoDa, la plateforme d'analyse de données de"
                                                    "réseaux sociaux.\nVeuillez choisir un fichier à analyser")
    analyze_file = gr.File(file_count='multiple', file_types=['.json'], interactive=True,
                           label="Sélectionnez un ou des fichiers à analyser")
    analyze_button = gr.Button(value="Lancer l'analyse")
    analysis = gr.Radio(choices=Radio_Choices,
                        value="Masquer",
                        label="Analyses",
                        info="Que voulez-vous analyser ?",
                        visible=False,
                        interactive=True)
    plot = gr.Plot(visible=False)
    slider = gr.Slider (visible=False)
    slider.change(change_r,inputs=[analysis,slider],outputs=plot)
    analysis.change(change_r, inputs=[analysis], outputs=[plot])
    interface.load(change_r, inputs=[analysis], outputs=[plot])
    analyze_button.click(start, outputs=[welcome_label, analyze_file, analyze_button, analysis])

interface.launch()
"""interface_init = gr.Interface(
    fn=start,
    inputs=["file"],
    outputs=None)
interface_init.launch()"""

"""print(f"Nombre de tweets analysés: {len(Tweet.all_tweets) + 1}")
print(get_top(Tweet.user_mentioned_sorted, 15))
print(get_top(Tweet.used_hashtag_sorted, 15))
print(get_top(Tweet.tweets_of_users_sorted, 15))
print(number_hashtag("#AI"))
print(publication_author('Chumlee'))"""

"""world_map()  # cette fonction demande beaucoup de temps pour s'exécuter et dépend de la connexion internet ! La
# console affiche l'avancement de cette dernière"""
