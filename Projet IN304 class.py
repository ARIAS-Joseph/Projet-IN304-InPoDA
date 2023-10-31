import json as js
from textblob import TextBlob
import spacy
import random


class Tweet:
    nb_tweets = 0
    used_hashtag = {}  # dictionnaire avec le nom du hashtag en clé et la liste des tweets contenant le hashtag en
    # valeur
    user_mentioned = {}  # dictionnaire avec le nom de l'utilisateur en clé et la liste des tweets mentionnant
    # l'utilisateur en valeur
    tweets_of_users = {}  # dictionnaire avec le nom de l'utilisateur en clé et la liste des tweets de l'utilisateur en
    # valeur
    all_tweets = []  # liste de tous les tweets

    def __init__(self, tweet: dict):
        Tweet.nb_tweets += 1
        tweet['Hashtags'] = []
        tweet['Mentions'] = []
        tweet['Topics'] = []
        tweet['Polarity'] = ''
        self.id = tweet['id']
        self.localisation = tweet['AuthorLocation']
        self.date = tweet['CreatedAt']
        self.rt = tweet['RetweetCount']
        self.langue = tweet['TweetLanguage']
        self.texte = tweet['TweetText']
        self.hashtag = tweet['Hashtags']
        self.mention = tweet['Mentions']
        self.polarity = tweet['Polarity']
        self.topics = tweet['Topics']
        self.author = tweet['Author']
        self.extract_car('#')  # extraction des hashtags utilisés dans le tweet
        self.extract_car('@')  # extraction des utilisateurs mentionnés dans le tweet
        self.analyse_sentiment()  # analyse du sentiment du tweet (négatif, neutre ou positif)
        self.extract_topics()  # extraction des topics du tweet
        self.list_tweet_by_author()  # ajout du tweet au dictionnaire tweets_of_users avec en clé l'auteur du tweet
        Tweet.used_hashtag_trie = sorted(Tweet.used_hashtag.items(),
                                         key=lambda item: len(item[1]), reverse=True)  # création d'une liste des
        # hashtags présents dans les tweets analysés triée par ordre décroissant du nombre d'apparition du hashtag
        Tweet.user_mentioned_trie = sorted(Tweet.user_mentioned.items(),
                                           key=lambda item: len(item[1]), reverse=True)  # création d'une liste des
        # utilisateurs mentionnés dans les tweets analysés triée par ordre décroissant du nombre de mention de
        # l'utilisateur
        Tweet.all_tweets.append(self)

    @classmethod
    def instantiate_from_file(cls):
        """ Fonction qui instancie les tweets présents dans un fichier json
        """
        donnees = open('aitweets.json', 'r', encoding='UTF-8')
        liste_tweets = [js.loads(line) for line in donnees]

        # Noms d'utilisateurs qui seront ajoutés aux tweets afin de mieux répondre aux questions du projet étant donné
        # qu'aucun nom d'utilisateur n'est fourni (certains noms sont plus susceptibles d'apparaître souvent afin de
        # rendre l'analyse des données plus intéressante)
        users_names = [*['@The Fiend'] * 18, *['@Bray Wyatt'] * 66, *['@Shinsuke Nakamura'] * 11, *['@Cory'] * 20,
                       '@Chumlee', '@Linkenb', '@Jean_Valjean', '@Martin', '@Dupont', *['@IainLJBrown'] * 100,
                       *['@Paula_Piccard'] * 50, *['@nigewillson'] * 25, *['@machinelearnTec'] * 15, 'Karl_Marx',
                       *['@akbarth3great'] * 15, '@JoshuaBarbeau', '@sankrant', '@machinelearnflx', '@SpirosMargaris',
                       *['@Datascience__'] * 30, *['@Charles_Henry'] * 38, *['@UEYvelines'] * 78,
                       *['@union_etudiante_'] * 99]

        for i in range(len(liste_tweets)):
            liste_tweets[i]['Author'] = random.choice(users_names)

        for tweet in liste_tweets:
            Tweet(tweet)

        donnees.close()

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
            liste_car = self.mention
            used_car = Tweet.user_mentioned
            nom_car = 'Mention'
        elif car == "#":  # si on veut extraire les hashtags utilisés
            liste_car = self.hashtag
            used_car = Tweet.used_hashtag
            nom_car = 'Hashtags'
        fin_car = 0  # indice du dernier caractère du hashtag/utilisateur que l'on veut extraire
        while True:
            if car in txt[fin_car:]:
                index_car = txt.find(car, fin_car)  # indice du premier caractère du hashtag/utilisateur que l'on veut
                # extraire
                if index_car != len(txt) - 1:  # certains tweets étant coupés, on n'extrait pas les hashtags/utilisateur
                    # si ces derniers ne constituent uniquement le caractère '@' our '#'
                    for j in range(index_car + 1, len(txt)):
                        if j == len(txt) - 1:
                            if txt[j].isalnum() or txt[j] == '_':
                                fin_car = j + 1
                            else:
                                fin_car = j
                            break
                        elif txt[j] != '_' and not txt[j].isalnum() or txt[j] == '.':
                            fin_car = j
                            break
                    nom_car = txt[index_car:fin_car]
                    if nom_car != car:
                        liste_car.append(nom_car)
                        if nom_car in used_car:
                            used_car[nom_car].append(self)
                        else:
                            used_car[nom_car] = [self]
                    else:
                        break
                else:
                    break
            else:
                break

    def analyse_sentiment(self):
        """Fonction qui analyse le sentiment d'un tweet (négatif, neutre ou positif)
        """
        polarity = TextBlob(self.texte).sentiment.polarity
        if polarity < 0:
            self.polarity = 'Negative'
        elif polarity == 0:
            self.polarity = 'Neutral'
        else:
            self.polarity = 'Positive'

    def extract_topics(self):
        pass

    def list_tweet_by_author(self):
        """Fonction qui ajoute le tweet à la liste des tweets d'un utilisateur
        """
        try:
            Tweet.tweets_of_users[self.author].append(self)
        except KeyError:
            Tweet.tweets_of_users[self.author] = [self]


def top(liste: list, k: int):
    """Top k hashtags ou Top k utilisateurs mentionnés

    Fonction qui affiche les top k hashtags ou les tops k utilisateurs mentionnés

    Paramètres
    ----------
    liste : list
        liste des hashtags et leurs occurrences ou liste des mentions d'utilisateurs et leurs occurrences
    k : int
        les k hashtags ou utilisateurs qui reviennent le plus

    """

    for i in range(0, k):
        try:
            if liste[i][0][0] == '#':
                top = 'hashtag'
                mention = 'occurrence'
            elif liste[i][0][0] == '@':
                top = 'utilisateur mentionné'
                mention = 'mention'
            print(
                f"Top {i + 1} {top} : {liste[i][0]} avec {len(liste[i][1])} {mention}"
                f"{'s' if len(liste[i][1]) > 1 else ''}")
        except IndexError:
            pass


def nombre_hashtag(hashtag: str):
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
    for tweet in Tweet.tweets_of_users[author]:
        print(tweet.texte)


Tweet.instantiate_from_file()
print(Tweet.nb_tweets)
print(top(Tweet.user_mentioned_trie, 10))
print(top(Tweet.used_hashtag_trie, 10))
print(nombre_hashtag("#AI"))
"""print(publication_author('The Fiend'))
"""
