import argparse
import logging.config
import os
import pprint

import corpus_reader as reader


def main(annotations_file, max_insts=-1):
    # train, dev, test = reader.read_train_dev_test_corpus(annotations_file, max_insts=max_insts)
    articles = reader.read_corpus(annotations_file, max_insts=max_insts)

    # number of wikipedia articles
    titles = set([])
    for key in articles.keys():
        titles.add(key)
    print("number of wikipedia articles: " + str(len(titles)))
    print()

    # average number of wikipedia sections per article
    section_list = []
    section_count = 0
    total_count = 0
    for key in articles.keys():
        for i in range(len(articles[str(key)])):
            section_count += 1
            total_count += 1
        section_list.append(section_count)
        section_count = 0
    print("average number of wikipedia sections per article: " + str(total_count / len(titles)))
    print()

    # number of possessors and years per article (2 numbers)
    info_dict = {}
    counter = 1
    num_possessors = 0
    num_years = 0
    for key in articles.keys():
        for i in range(len(articles[str(key)])):
            num_possessors += 1
            num_years += 1
        str_name = "article " + str(counter)
        info_dict[str_name] = {"possessors": num_possessors, "years": num_years}
        counter += 1
        num_possessors = 0
        num_years = 0
    print("number of possessors and years per article (2 numbers): ")
    print(info_dict)
    print()

    # number of unique possessors and unique years per article (2 numbers)
    info_u_dict = {}
    counter_u = 1
    possessors_u_set = set([])
    years_u_set = set([])
    for key in articles.keys():
        for i in range(len(articles[str(key)])):
            possessors_u_set.add(articles[str(key)][i].possessor)
            years_u_set.add(articles[str(key)][i].year)
        str_name = "article " + str(counter_u)
        info_u_dict[str_name] = {"u possessors ": len(possessors_u_set), "u years ": len(years_u_set)}
        counter_u += 1
        possessors_u_set = set([])
        years_u_set = set([])
    print("number of unique possessors and unique years per article (2 numbers): ")
    print(info_u_dict)
    print()

    # number of unique possessor, year pairs (1 number)
    pair_set = set([])
    for key in articles.keys():
        for i in range(len(articles[str(key)])):
            tuple_pair = (articles[str(key)][i].possessor, articles[str(key)][i].year)
            pair_set.add(tuple_pair)
    print("number of unique possessor, year pairs (1 number): ")
    print(len(pair_set))


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

    main(args.ANNOTATIONS_FILE, args.max_articles)
