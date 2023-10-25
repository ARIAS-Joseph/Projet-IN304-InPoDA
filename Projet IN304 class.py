import json as js
import operator
from textblob import TextBlob

donnees = open('aitweets.json', 'r', encoding='UTF-8')
data = [js.loads(line) for line in donnees]

donnees.close()


class Tweet:
    nb_tweets = 0
    used_hashtag = {}
    user_mentioned = {}

    def __init__(self, tweet: dict):
        Tweet.nb_tweets += 1
        tweet['Hashtags'] = []
        tweet['Mentions'] = []
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
        self.extract_car('#')
        self.extract_car('@')
        self.analyse_sentiment()

    def extract_car(self, car):
        """Fonction qui extrait les hashtags utilisés ou les utilisateurs
        mentionnés dans le tweet à partir d'une base de données et les ajoute
        à la base de données

        Parameters
        ----------
        car : str
            Le caractère que l'on recherche (# si on cherche les hashtags et @
            si on cherche les utilisateurs"
        """

        txt = self.texte
        if car == "@":
            liste_car = self.mention
            used_car = Tweet.user_mentioned
            nom_car = 'Mention'
        elif car == "#":
            liste_car = self.hashtag
            used_car = Tweet.used_hashtag
            nom_car = 'Hashtags'
        fin_car = 0
        while True:
            if car in txt[fin_car:]:
                index_car = txt.find(car, fin_car)
                if index_car != len(txt) - 1:
                    for j in range(index_car + 1, len(txt)):
                        if j == len(txt) - 1:
                            if txt[j].isalnum():
                                fin_car = j + 1
                            else:
                                fin_car = j
                            break
                        elif txt[j] != '_' and not txt[j].isalnum() \
                                or txt[j] == '.':
                            fin_car = j
                            break
                    nom_car = txt[index_car:fin_car]
                    if nom_car != car:
                        liste_car.append(nom_car)
                        if nom_car in used_car:
                            used_car[nom_car].append(self.id)
                        else:
                            used_car[nom_car] = [self.id]
                    else:
                        break
            else:
                break

    def analyse_sentiment(self):
        polarity = TextBlob(self.texte).sentiment.polarity
        if polarity < 0:
            self.polarity = 'Negative'
        elif polarity == 0:
            self.polarity = 'Neutral'
        else:
            self.polarity = 'Positive'


def top(liste, k):
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
        if liste[i][0][0] == '#':
            top = 'hashtag'
        elif liste[i][0][0] == '@':
            top = 'utilisateur mentionné'
        print(f"Top {i + 1} {top} : {liste[i][0]} avec {len(liste[i][1])} occurrence{'s' if len(liste[i][1]) > 1 else ''}")


def nombre_hashtag(liste, hashtag):
    """Nombre de publications par hashtag

    Fonction qui affiche le nombre de publications pour un hashtag donné

    Paramètres
    ----------
    liste : list
        liste des hashtags
    hashtag : str
        nom du hashtag que l'on veut compter

    """

    for i in range(len(liste)):
        if liste[i][0] == hashtag:
            print(f"Le hashtag {hashtag} apparaît dans {len(liste[i][1])} publication{'s' if len(liste[i][1]) > 1 else ''}")


liste_tweets = [Tweet(data[i]) for i in range(len(data))]
Tweet.used_hashtag = sorted(Tweet.used_hashtag.items(),
                            key=lambda item: len(item[1]), reverse=True)
Tweet.user_mentioned = sorted(Tweet.user_mentioned.items(),
                              key=lambda item: len(item[1]), reverse=True)

print(Tweet.nb_tweets)
print(top(Tweet.user_mentioned, 10))
print(top(Tweet.used_hashtag, 10))
print(nombre_hashtag(Tweet.used_hashtag, "#AI"))
