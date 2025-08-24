from fastopic import FASTopic
from topmost.preprocess import Preprocess
import os
import spacy
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])


# directory with the texts
data_directory = '../data_ai_titles'

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
    "grant", "insert", "generalthe", "thank", "going", "know", "right", "just", "need", "people", "like", "briefing", "debriefing",
    "briefings", "brief", "debrief", "aint", "arent", "cant", "couldve", "couldnt", "didnt", "doesnt", "dont",
    "gonna", "gotta", "hadnt", "hasnt", "havent", "hed", "hell", "hes", "howd", "howll", "hows", "id", "ill", "im", "ive", "isnt", "itd", "itll", "its",
    "lets", "mightve", "mightnt", "mustve", "mustnt", "neednt", "shant", "shed", "shell", "shes", "shouldve", "shouldnt", "somebodyll", "somebodys",
    "someonell", "someones", "thatd", "thatll", "thats", "thered", "therell", "theres", "theyd", "theyll", "theyre", "theyve", "wasnt", "wed", "well",
    "were", "werent", "whatd", "whatll", "whats", "whatve", "whens", "whered", "wheres", "whereve", "whod", "wholl", "whos", "whove", "whyd", "whyre",
    "whys", "wont", "wouldve", "wouldnt", "yall", "youd", "youll", "youre", "youve"
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

def model(k):
    docs = all_docs

    preprocess = Preprocess(stopwords=combined_stopwords, min_length=4, max_doc_freq=0.7)
    model = FASTopic(k, preprocess)
    top_words, doc_topic_dist = model.fit_transform(docs)

    fig = model.visualize_topic(top_n=k)
    fig.update_layout(title_text="Topic-Word Distributions")
    fig.show()


num_topics = [3,5,7,9]

for k in num_topics:
    model(k)