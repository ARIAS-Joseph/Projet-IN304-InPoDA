import json as js
import operator

donnees = open('aitweets.json', 'r', encoding='UTF-8')
data = [js.loads(line) for line in donnees]

donnees.close()


class Tweet:

    nb_tweets = 0
    used_hashtag = {}

    def __init__(self, tweet=dict):
        Tweet.nb_tweets += 1
        tweet['Hashtags'] = []
        self.id = tweet['id']
        self.localisation = tweet['AuthorLocation']
        self.date = tweet['CreatedAt']
        self.rt = tweet['RetweetCount']
        self.langue = tweet['TweetLanguage']
        self.texte = tweet['TweetText']
        self.hashtag = tweet['Hashtags']
        self.extact_hashtag()

    def extract_hashtag(self):
        """Fonction qui extrait les hashtags utilisés dans le tweet à partir d'une base de données et les ajoute à la
        base de données
        """

        txt = self.texte
        liste_hashtag = self.hashtag
        fin_hashtag = 0
        while True:
            if '#' in txt[fin_hashtag:]:
                index_hashtag = txt.find('#', fin_hashtag)
                if index_hashtag != len(txt)-1:
                    for j in range(index_hashtag+1, len(txt)):
                        if j == len(txt)-1:
                            if txt[j].isalnum():
                                fin_hashtag = j+1
                            else:
                                fin_hashtag = j
                            break
                        elif txt[j] != '_' and not txt[j].isalnum() or txt[j] == '.':
                            fin_hashtag = j
                            break
                    nom_hashtag = txt[index_hashtag:fin_hashtag]
                    if nom_hashtag != '#':
                        liste_hashtag.append(nom_hashtag)
                        if nom_hashtag in Tweet.used_hashtag:
                            Tweet.used_hashtag[nom_hashtag] += 1
                        else:
                            Tweet.used_hashtag[nom_hashtag] = 1
                    else:
                        break
            else:
                break


liste_tweets = [Tweet(data[i]) for i in range(len(data))]
Tweet.used_hashtag = sorted(Tweet.used_hashtag.items(), key=operator.itemgetter(1), reverse=True)

print(Tweet.nb_tweets)
print(Tweet.used_hashtag)
