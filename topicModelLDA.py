__author__ = 'IH'
__project__ = 'processMOOC'

import re
from html.parser import HTMLParser
from stop_words import get_stop_words
from gensim import corpora, models

class LDAtopicModel(object):
    """
    Class contains an LDA topic model for one set of documents.
    Mostly exists as a way to access (and setup) topic_names
    """
    number_of_topics = 1
    docs = []
    topic_names = []
    lda = None
    FORMAT_LINE = "--------------------"

    def __init__(self, nt, docs_as_bow):
        """
        Initialize class with documents to train the model on
        :param docs_as_bow: a list of text documents as bags of words
        :return: None
        """
        self.docs = docs_as_bow
        self.number_of_topics = nt
        self.create_lda()

    def create_lda(self):
        """
        Runs all posts through an LDA topic model, to determine the basic topic of the post.
        http://chrisstrelioff.ws/sandbox/2014/11/13/getting_started_with_latent_dirichlet_allocation_in_python.html
        http://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
        :param all_docs: a list of bag of words (each string split into its own list)
        :return: None
        """
        print("Creating LDA topic model from " + str(len(self.docs)) + " documents.")
        num_topics = self.number_of_topics
        chunk_size = int(len(self.docs)/100)
        if chunk_size < 1:
            chunk_size = 1  # small number of sentences

        all_tokens = sum(self.docs, [])
        # process our stop words like all our words have been processed
        tokens_stop = []
        for word in get_stop_words('en'):
            tokens_stop.extend(self.to_bow(word))

        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        # remove words that appear only once or are stop words
        texts = [[word for word in sentence if word not in tokens_once and word not in tokens_stop] for sentence in self.docs]

        # constructing topic model
        dict_lda = corpora.Dictionary(texts)
        mm_corpus = [dict_lda.doc2bow(text) for text in texts]
        self.lda = models.ldamodel.LdaModel(corpus=mm_corpus, id2word=dict_lda, num_topics=num_topics, update_every=1, chunksize=chunk_size, passes=1)
        #topics = lda.print_topics(self.number_of_topics)

        # get list of lda topic names
        print(self.FORMAT_LINE)
        # printing each topic
        for topic in self.lda.print_topics(self.number_of_topics):
            print(topic)
        print(self.FORMAT_LINE)

        print("\n")
        print("- Begin naming topics -")
        # naming each topic
        i = 1
        for topic in self.lda.print_topics(self.number_of_topics):
            print("\t(" + str(i) + ") "+ topic)
            self.topic_names.append(input("> A name for topic (" + str(i) + "): "))
            i += 1
        print("Done creating LDA topic model")


    def predict_topic(self, document):
        """
        Predict the most likely topic for the given document
        :param document: the string to predict the topic for
        :return: the string topic name
        """
        if self.lda is None:
            print("ERROR in lda_topic_model.predict_topic(): Need to create_lda() before predicting topics.")
        dict_lda = getattr(self.lda, 'id2word')
        lda_vector = self.lda[dict_lda.doc2bow(self.to_bow(document))]
        return self.topic_names[max(lda_vector, key=lambda item: item[1])[0]]
        #print(max(lda_vector, key=lambda item: item[1])[0])
        #print(lda.print_topic(max(lda_vector, key=lambda item: item[1])[0]))  # prints the most prominent LDA topic

    @staticmethod
    def clean_string(sentence):
        """
        Clean the string by removing all punctuation and HTML
        http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
        :param sentence: the string potentially containing HTML and other non-alphanumerics
        :return: the string cleaned of all tags, undesirables as a list of strings (bag of words)
        """
        s = MLStripper()
        s.feed(sentence)
        no_html = s.get_data()
        # This code apparently removes all text in a string without any HTML
        if len(no_html) < 10:
            no_html = sentence
        cleaned = re.sub(r'[^a-zA-Z\' ]+', '', no_html)  # Leaving in letters and apostrophes
        # TODO: How to handle URLs? 'httplightsidelabscomwhatresearch'
        # TODO: Contractions (i.e., can't) are okay, but possession isn't (i.e., Carolyn's)
        # TODO: Should removed characters be replaced with a space? Or no space (as is)?
        return cleaned.lower()

    @staticmethod
    def to_bow(sentence):
        """
        Turn given string into a bag of words
        :param sentence: the string to turn into a list
        :return: the string  as a list of strings (bag of words)
        """
        texts = [word for word in sentence.split()]  # turning each word into an item in a list
        return texts

class MLStripper(HTMLParser):
    """
    A class for stripping HTML tags from a string
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
