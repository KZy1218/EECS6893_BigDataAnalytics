import sys, pyspark, re, nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

# preprocessing utility function
stop_words = stopwords.words('english')

def preprocess(lines):
    def word_preprocess(w):
        return re.sub("[^A-Za-z0-9]+", "", w.lower())
    temp = [word_preprocess(word) for word in lines.split()]
    return [w for w in temp if w not in stop_words and w != ""]


if len(sys.argv) != 3:
    raise Exception("Exactly 2 arguments are required: <inputUri> <outputUri>")

inputUri = sys.argv[1]
outputUri = sys.argv[2]

sc = pyspark.SparkContext()
lines = sc.textFile(inputUri)

PROCESS = True
words = lines.flatMap(preprocess) if PROCESS else lines.flatMap(lambda l: l.split())

wordCount = words.map(lambda w: (w, 1)).reduceByKey(lambda c1, c2: c1 + c2)
wordCount_sorted = wordCount.map(lambda x: (x[1], x[0])).sortByKey(False)
wordCount_sorted.collect()

print()
print(">>>>>>>>>>> Top 10 frequent words without text preprocessing >>>>>>>>>>>")
print(wordCount_sorted.take(10))
print(">>>>>>>>>>> End >>>>>>>>>>> \n")

wordCount_sorted.saveAsTextFile(outputUri)