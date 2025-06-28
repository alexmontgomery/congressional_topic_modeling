import pandas as pd
import gensim.corpora as corpora
import gensim
import spacy
import os
from gensim.models import CoherenceModel
from pprint import pprint
from time import time
from gensim.test.utils import datapath
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load("en_core_web_sm")

custom_stopwords = [
    "artificial", "intelligence", "ai", "fiscal", "year", "secretary", "united", "states", "shall", "program",
    "i", "ii", "iii", "iv", "v", "national", "development", "public", "private", "report", "research", "mr",
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
    "increase", "decrease", "enhance", "strengthen", "support", "new", "old", "use", "sec",
    "including", "available", "following", "activities", "date", "information", "funds", "funding", "programs"
]

for word in custom_stopwords:
    STOP_WORDS.add(word)


def main():
    def sentence_to_words(text):
        for words in text:
            # deacc=True removes punctuations
            yield gensim.utils.simple_preprocess(str(words), deacc=True)

    def coherence_test(docs, start_topics, end_topics, phrase_length=1):

        def make_bigrams(texts):
            return [bigram_mod[doc] for doc in texts]

        def make_trigrams(texts):
            return [trigram_mod[bigram_mod[doc]] for doc in texts]

        # data = text.values.tolist()
        data_words = list(sentence_to_words(docs))

        #Remove stopwords
        data_words = [[word for word in row if word not in custom_stopwords] for row in data_words]


        print(data_words)
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

        if phrase_length == 1:
            data_words = data_words
        if phrase_length == 2:
            bigram_mod = gensim.models.phrases.Phraser(bigram)
            data_words = make_bigrams(data_words)
        if phrase_length == 3:
            bigram_mod = gensim.models.phrases.Phraser(bigram)
            trigram_mod = gensim.models.phrases.Phraser(trigram)
            data_words = make_bigrams(data_words)
            data_words = make_trigrams(data_words)

        id2word = corpora.Dictionary(data_words)
        id2word.filter_extremes(no_below=10, no_above=0.4)
        texts = data_words
        corpus = [id2word.doc2bow(text) for text in texts]
        
        score = []
        for num_topics in range(start_topics, end_topics + 1):
            lda_model = gensim.models.LdaModel(corpus=corpus,
                                               id2word=id2word,
                                               num_topics=num_topics)
            coherence_model_lda = CoherenceModel(model=lda_model, texts=data_words, dictionary=id2word, coherence='c_v')
            coherence_lda = coherence_model_lda.get_coherence()
            score.append(coherence_lda)
            print('Coherence Score: ', num_topics, ' ', coherence_lda)
        max_value = max(score)
        return score.index(max_value) + 2, corpus, id2word


    start_time = time()


    # file = r'D:\PyCharmProjects\topic_classification\reddit_artificial_intelligence_cleaned.csv'
    # df = pd.read_csv(file)
    # column = 'title_self_text_cleaned'

    # directory with the texts
    data_directory = '../data_no_dups'

    # passed to coherence_test
    all_texts = []

    # file counter for testing w/ a subset of the directory
    file_counter = 0
    max_files = 5808

    for root, dirs, files in os.walk(data_directory):
        for filename in files:
            if filename.endswith(".txt"):
                full_path = os.path.join(root, filename)
                try:
                    with open(full_path, 'r') as file:
                        contents = file.read()
                        all_texts.append(contents)
                        #file_counter += 1

                    if file_counter >= max_files:
                        break

                except Exception as e:
                    print(f"An error occurred while reading {full_path}: {e}")
        if file_counter >= max_files:
            break

    num_topics, corpus, id2word = coherence_test(all_texts[2000:2500], start_topics=4, end_topics=12, phrase_length=3)
    print('Maximum number of topics, based on coherence score: ', num_topics)
    lda_model = gensim.models.LdaModel(corpus=corpus,
                                       id2word=id2word,
                                       #Change num_topics (after the parentheses) below for manual number of topics
                                       num_topics=num_topics)
    pprint(lda_model.print_topics())
    end_time = time()
    print('Total time elapsed: ', str(end_time - start_time))

    # all_topics = lda_model.get_document_topics(corpus, minimum_probability=0.0)
    # all_topics_csr = gensim.matutils.corpus2csc(all_topics)
    # all_topics_numpy = all_topics_csr.T.toarray()
    # all_topics_df = pd.DataFrame(all_topics_numpy)
    # all_topics_df['max_topic'] = all_topics_df.idxmax(axis=1)
    # print(all_topics_df)
    # df = pd.concat([df, all_topics_df], axis=1)
    # save_file = file.split('.')[0] + '_LDA_topics.csv'
    # temp_file = datapath(save_file.split('.')[0])
    # lda_model.save(temp_file)
    # df.to_csv(save_file, index=False)


if __name__ == "__main__":
    main()

