YES = '1'
NO = '0'
LABELS = [YES, NO]

BEF = u"BEF"
DUR = u"DUR"
AFT = u"AFT"
TMP_ANCHORS = [BEF, DUR, AFT]

POSS = u"POSSESSOR"
YEAR = u"YEAR"


class Annotation:
    def __init__(self, possessor, year, labels):
        assert set(TMP_ANCHORS) == set(labels.keys())

        self.possessor = possessor
        self.year = year
        self.labels = labels

    def __str__(self):
        labels = ["%3s: %1s" % (k, v) for k, v in self.labels.items()]
        ents = "\n".join(map(str, ["  %s %s" % (str(ent.label_), ent) for ent in self.possessor.doc.ents]))
        return "ARTICLE: %s\n" \
               "SECTION: %s\n" \
               "SECTION CONTENT: %s\n" \
               "ALL entities:\n%s\n" \
               "LABELS | possessor|year: %s |%s|%s|" % (self.possessor.doc._.article_title_doc,
                                                        self.possessor.doc._.section_title_doc,
                                                        self.possessor.doc,
                                                        ents,
                                                        labels, self.possessor, self.year)