import spacy
import urllib
from gutenberg.cleanup import strip_headers

# save url as .txt file
url = "https://www.gutenberg.org/files/57886/57886-0.txt"
info = urllib.request.urlopen(url)
text = ""

# parse and add the text
for line in info:
    text += line.decode("utf-8")

# strip the headers off the text
text = strip_headers(text).strip()

# create a language model instance
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)

# problem 1 - number of sentences
num_sentences = len(list(doc.sents))
print("number of sentences: " + str(num_sentences))

# problem 2 - number of words
num_tokens = len(doc)
print("number of words: " + str(num_tokens))

# problem 3 - average number of words per sentence
avg_tokens_sentence = num_tokens / num_sentences
print("average number of words per sentence: " + str(avg_tokens_sentence))

# problem 4 - number of unique parts of speech tags
pos_tags = []
for token in doc:
    pos_tags.append(token.pos_)
unique_pos = len(set(pos_tags))
print("number of unique parts of speech tags: " + str(unique_pos))

# problem 5 - 5 most frequent part of speech tags
pos_counts = []
for pos in set(pos_tags):
    pos_counts.append(pos_tags.count(pos))
most_freq_pos = pos_counts
most_freq_pos.sort()
most_freq_pos = most_freq_pos[-5: len(most_freq_pos)]
print("counts of 5 most frequent parts of speech tags: " + str(most_freq_pos))

# problem 6 - least frequent part of speech tags
least_freq_pos = pos_counts
least_freq_pos.sort()
least_freq_pos = least_freq_pos[0: 5]
print("counts of 5 least frequent parts of speech tags: " + str(least_freq_pos))

# problem 7 - number of named entities of each type
# classification of each type of real-world object with proper names
all_entities = []
for token in doc:
    if token.ent_type_:
        all_entities.append(token.ent_type_)
entities_dict = {}
for entity in set(all_entities):
    entities_dict.update({entity: all_entities.count(entity)})
print("named entities and counts: " + str(entities_dict))

# problem 8 - number of sentences with at least one negative syntactic dependency
# negative syntactic dependency words are words that are like "no, not, never"
num_dep_sentences = 0
for sentence in list(doc.sents):
    num_dep_tokens = 0
    for token in sentence:
        if token.dep_ == "neg":
            num_dep_tokens += 1
    if num_dep_tokens >= 1:
        num_dep_sentences += 1
print("number of sentences with at least one negative syntactic dependency: " + str(num_dep_sentences))

# problem 9 - number of sentences whose root is the verb went
num_root_sentences = 0
for sentence in list(doc.sents):
    if str(sentence.root) == "went":
        num_root_sentences += 1
print("number of sentences whose root is the verb 'went': " + str(num_root_sentences))
