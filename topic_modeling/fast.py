from fastopic import FASTopic
from topmost.preprocess import Preprocess
import os
import spacy
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])


# directory with the texts
data_directory = '../data_no_dups'

all_docs = []

custom_stopwords = [
    "artificial", "intelligence", "ai", "fiscal", "year", "secretary", "united", "states", "shall", "program",
    "i", "ii", "iii", "iv", "v", "national", "development", "public", "private",
    "congress", "committee", "hearing", "subcommittee", "resolution", "legislation", "amendment",
    "bill", "act", "law", "session", "floor", "chairman", "ranking", "member", "representative",
    "senator", "house", "senate", "chamber", "vote", "yeas", "nays", "motion", "debate", "journal",
    "hereby", "whereas", "therefore", "pursuant", "be", "it", "resolved", "enacted", "provided",
    "section", "title", "subtitle", "clause", "paragraph", "article", "subsection", "part", "item",
    "effective", "enactment", "statute", "code", "provision", "authorized",
    "notwithstanding", "heretofore", "hereinafter", "aforementioned", "said", "such", "therein",
    "thereof", "thereinabove", "hereof", "thereunder", "forthwith", "in", "accordance", "with",
    "compliance", "implementation", "administrator", "agency", "department",
    "federal", "state", "local", "government", "agency", "secretary", "president", "vice",
    "governor", "mayor", "department", "office", "administration", "commission", "bureau",
    "amend", "authorize", "establish", "require", "appropriated", "fund", "implement", "regulate",
    "prohibit", "repeal", "promote", "designate", "allocate", "extend", "ensure", "encourage",
    "increase", "decrease", "enhance", "strengthen", "support", "new", "old", "use", "sec", "asxmlhtmlxmlhtml",
    "think", "really", "sort", "okay", "maybe", "subparagraph", "inserting", "striking", "heading", "amended", "http", "https",
    "grant", "insert", "generalthe"
]
combined_stopwords = custom_stopwords + list(ENGLISH_STOP_WORDS)


for root, dirs, files in os.walk(data_directory):
    for filename in files:
        if filename.endswith(".txt"):
            full_path = os.path.join(root, filename)
            try:
                with open(full_path, 'r') as file:
                    contents = file.read()
                    all_docs.append(contents)

            except Exception as e:
                print(f"An error occurred while reading {full_path}: {e}")


# split the corpus (e.g. (0, 5809) should cover all in one pass)
partitions = [(0, 1500), (1500, 3000), (3000, 4500), (4500, 5809)]

# number of topics
k = 8

for p in partitions:

    docs = all_docs[p[0]:p[1]]

    preprocess = Preprocess(stopwords=combined_stopwords, min_length=4, max_doc_freq=0.7, min_term=10)
    model = FASTopic(k, preprocess)
    top_words, doc_topic_dist = model.fit_transform(docs)

    fig = model.visualize_topic(top_n=k)
    fig.update_layout(title_text=f"Topic-Word Distributions: Documents {p[0]}-{p[1]} of Corpus")
    fig.show()

    fig = model.visualize_topic_weights(top_n=k, height=500)
    fig.update_layout(title_text=f"Topic Weights: Documents {p[0]}-{p[1]} of Corpus")
    fig.show()
