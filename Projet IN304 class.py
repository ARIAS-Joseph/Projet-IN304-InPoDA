import json as js
import operator

donnees = open('aitweets.json', 'r', encoding='UTF-8')
data = [js.loads(line) for line in donnees]

donnees.close()


class Tweet:

    nb_tweets = 0
    used_hashtag = {}
    user_mentioned = {}

    def __init__(self, tweet=dict):
        Tweet.nb_tweets += 1
        tweet['Hashtags'] = []
        tweet['Mentions'] = []
        self.id = tweet['id']
        self.localisation = tweet['AuthorLocation']
        self.date = tweet['CreatedAt']
        self.rt = tweet['RetweetCount']
        self.langue = tweet['TweetLanguage']
        self.texte = tweet['TweetText']
        self.hashtag = tweet['Hashtags']
        self.mention = tweet['Mentions']
        self.extract_car('#')
        self.extract_car('@')

    def extract_car(self, car):
        """Fonction qui extrait les hashtags utilisés ou les utilisateurs mentionnés dans le tweet à partir d'une base
        de données et les ajoute à la base de données
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
                if index_car != len(txt)-1:
                    for j in range(index_car+1, len(txt)):
                        if j == len(txt)-1:
                            if txt[j].isalnum():
                                fin_car = j+1
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
                            used_car[nom_car] += 1
                        else:
                            used_car[nom_car] = 1
                    else:
                        break
            else:
                break


liste_tweets = [Tweet(data[i]) for i in range(len(data))]
Tweet.used_hashtag = sorted(Tweet.used_hashtag.items(), key=operator.itemgetter(1), reverse=True)
Tweet.user_mentioned = sorted(Tweet.user_mentioned.items(), key=operator.itemgetter(1), reverse=True)

print(Tweet.nb_tweets)
print(Tweet.used_hashtag)
print(Tweet.user_mentioned)
