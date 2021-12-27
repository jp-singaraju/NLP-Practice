import argparse
import logging.config
import collections
import re
import pprint
import pandas as pd
import random
import os

import spacy
from spacy.matcher import Matcher

import data_structures

TRAIN_PERCENT = 0.8
DEV_PERCENT = 0.2
TEST_PERCENT = 0.2

spacy.tokens.Doc.set_extension('id', default="")
spacy.tokens.Doc.set_extension('article_title_doc', default="")
spacy.tokens.Doc.set_extension('section_title_doc', default="")
spacy.tokens.Doc.set_extension('annotations', default=[])

print("Loading spacy...")
nlp = spacy.load('en_core_web_sm')  # , disable=['tagger', 'parser'])
nlp.entity.add_label(data_structures.YES)
nlp.entity.add_label(data_structures.NO)
nlp.entity.add_label(data_structures.POSS)
nlp.entity.add_label(data_structures.YEAR)
print("... spacy loaded")


def read_corpus(annotations_file, max_insts=-1):
    binary2categorical = lambda i: str(i)

    annotations = pd.read_csv(annotations_file,
                              converters={'Before': binary2categorical,
                                          'During': binary2categorical,
                                          'After': binary2categorical},
                              usecols=['Wiki_title', 'Section_title', 'Section_contents', 'Same/Diff',
                                       'Possessor', 'Year', 'Before', 'During', 'After'])
    print(annotations.describe(include='all'))

    articles = collections.defaultdict(list)
    article_titles, section_titles, section_contents, possessors_nlp = {}, {}, {}, {}
    i = 0
    for _, annotation in annotations.iterrows():
        # Store processed document and reuse, just to save time (~ 80%)
        if annotation['Wiki_title'] not in article_titles:
            article_titles[annotation['Wiki_title']] = nlp(annotation['Wiki_title'])
        if annotation['Section_title'] not in section_titles:
            section_titles[annotation['Section_title']] = nlp(annotation['Section_title'])
        if annotation['Section_contents'] not in section_contents:
            section_contents[annotation['Section_contents']] = nlp(annotation['Section_contents'])

        article_title = article_titles[annotation['Wiki_title']]
        section_title = section_titles[annotation['Section_title']]
        section_content = section_contents[annotation['Section_contents']]

        section_content._.id = annotation['Wiki_title']
        section_content._.article_title_doc = article_title
        section_content._.section_title_doc = section_title

        poss_matcher = Matcher(nlp.vocab)
        possessor_text = str(annotation['Possessor'])
        # FIXME Tweak to make it work, otherwise spacy tokenization detects only two tokens in
        #   "The Paris-"
        if possessor_text[-1] == '-':
            possessor_text = possessor_text[:-1]
        # FIXME Tweak to fix issue with possesssor with the current annotations
        if possessor_text.startswith(u"David") and \
                annotation['Wiki_title'] == u"Bathsheba at Her Bath (Rembrandt)":
            possessor_text = u"David"

        if possessor_text not in possessors_nlp:
            possessors_nlp[possessor_text] = nlp(possessor_text)
        possessor_doc = possessors_nlp[possessor_text]

        poss_matcher.add('POSSESSOR', None, [{'ORTH': token.text} for token in possessor_doc])
        # FIXME Tweak to deal with a weird possessor in the current annotations
        poss_matcher.add('POSSESSOR', None, [{'ORTH': u"Louis"}, {}, {'ORTH': u"XII"}])
        possessors = poss_matcher(section_contents[annotation['Section_contents']])

        if len(possessors) == 0:
            logging.critical("**** CRITICAL: missing possessor (?)")
            logging.critical(annotation)
            logging.critical(len(possessor_doc))
            for token in possessor_doc:
                logging.critical(token)
            for token in section_content:
                logging.critical(token)
            continue

        year_tokens = [token for token in section_content if re.search(str(annotation['Year']), token.text)]
        assert len(year_tokens) > 0, "%s\n%s" % (annotation['Year'], section_content)

        # FIXME for now, taking the first possessor and the first year
        possessor = possessors[0]
        year = year_tokens[0]
        # print possessor, year, annotation['Before'], annotation['During'], annotation['After']
        possessor = spacy.tokens.Span(section_content, possessor[1], possessor[2],
                                      label=section_content.vocab.strings[data_structures.POSS])
        year = spacy.tokens.Span(section_content, year.i, year.i + 1,
                                 label=section_content.vocab.strings[data_structures.YEAR])
        labels = {data_structures.BEF: annotation['Before'],
                  data_structures.DUR: annotation['During'],
                  data_structures.AFT: annotation['After']}
        annot = data_structures.Annotation(possessor, year, labels)
        articles[annotation['Wiki_title']].append(annot)

        i += 1
        if max_insts != -1 and i > max_insts:
            break

    return articles


def read_train_test_corpus(annotations_file, max_insts=-1):
    articles = read_corpus(annotations_file, max_insts=max_insts).values()
    print(type(articles))
    random.seed(5)
    random.shuffle(articles)
    num_tr = int(len(articles) * TRAIN_PERCENT)
    articles_tr = articles[:num_tr]
    articles_te = articles[num_tr:]
    assert len(articles_tr) > 0
    assert len(articles_te) > 0
    for article in articles_tr:
        print("TRAIN", article[0].possessor.doc._.id)
    for article in articles_te:
        print("TEST", article[0].possessor.doc._.id)

    return articles_tr, articles_te


def read_train_dev_test_corpus(annotations_file, max_insts=-1):
    articles = list(read_corpus(annotations_file, max_insts=max_insts).values())

    random.seed(23621)
    random.shuffle(articles)
    num_tr = int(len(articles) * TRAIN_PERCENT)
    num_de = int(num_tr * DEV_PERCENT)
    if num_de == 0:
        num_tr -= 1
        num_de = 1
    assert num_tr > 0
    assert num_de > 0
    assert len(articles) > (num_tr + num_de)

    print(len(articles), num_tr, num_de)
    articles_tr = articles[:num_tr - num_de]
    articles_de = articles[num_tr - num_de:num_tr]
    articles_te = articles[num_tr:]
    print("\nFiles in train, dev and test:")
    for article in articles_tr:
        print("TRAIN", article[0].possessor.doc._.id)
    for article in articles_de:
        print("DEV", article[0].possessor.doc._.id)
    for article in articles_te:
        print("TEST", article[0].possessor.doc._.id)
    print()

    return articles_tr, articles_de, articles_te


def main(annotations_file, max_insts=-1):
    train, dev, test = read_train_dev_test_corpus(annotations_file, max_insts=max_insts)
    for insts in train:
        for inst in insts:
            print(inst)
            print()
    for insts in dev:
        for inst in insts:
            print(inst)
            print()
    for insts in test:
        for inst in insts:
            print(inst)
            print()


if __name__ == "__main__":
    file_dir = os.path.split(os.path.realpath(__file__))[0]
    LOGGING_CONF_FILE = os.path.join(file_dir, 'logging.conf')

    logging.config.fileConfig(LOGGING_CONF_FILE)
    logging.debug("Loaded configuration file %s" % LOGGING_CONF_FILE)

    parser = argparse.ArgumentParser(description='Read corpus')
    parser.add_argument("ANNOTATIONS_FILE",
                        help="File in csv format with the annotations")
    parser.add_argument("-m", "--max_articles", type=int, default=-1,
                        help="Read this many articles and quit")
    parser.add_argument("-s", "--stats", action='store_true',
                        help="Print stats instead of instances")

    args = parser.parse_args()
    logging.debug(pprint.pformat(args))

    main(args.ANNOTATIONS_FILE, max_insts=args.max_articles)
