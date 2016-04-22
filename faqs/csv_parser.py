import csv
import os
import sys
import unicodedata


class CsvConverter(object):

    def __init__(self, delimiter=',', quotechar='"'):
        self.delimiter = delimiter
        self.quotechar = quotechar

    def parse(self, csvfile, locale):
        if len(locale) != 2:
            raise ValueError("Locale must have a length of 2")
        locale = self._decode(locale)

        faqs = {
            "__current_faq__": None,
            "__current_topic__": None,
        }

        reader = csv.reader(
            csvfile, delimiter=self.delimiter, quotechar=self.quotechar)
        for i, row in enumerate(reader):
            if i < 3:
                continue  # skip first 3 rows
            self._handle_row(row, faqs, locale)

        del faqs["__current_faq__"]
        del faqs["__current_topic__"]
        return faqs

    def _decode(self, s):
        return s.decode("utf-8")

    def _handle_row(self, row, faqs, locale):
        current_faq = faqs.get("__current_faq__")
        current_topic = faqs.get("__current_topic__")

        new_faq = row[0].strip().replace("/", "")
        if new_faq and new_faq != current_faq:
            current_faq = faqs["__current_faq__"] = new_faq
            current_topic = None
            faqs[current_faq] = {}
        faq = faqs[current_faq]

        if row[4] == 'Back' or row[7] == 'Back' or len(row[7].strip()) == 0:
            return

        new_topic = row[4].strip()
        if new_topic and new_topic != current_topic:
            current_topic = faqs["__current_topic__"] = new_topic
            faq[current_topic] = []
            return
        topic = faq[current_topic]

        entry = RowEntry(
            locale, self._decode(row[6]), self._decode(row[10]),
            self._decode(row[15]))
        topic.append(entry)
        return

    def save(self, category, faqs):
        for faq in sorted(faqs.keys()):
            output_file = os.path.join(category, "%s.csv" % faq)
            with open(output_file, "wb") as f:
                writer = csv.writer(f)
                writer.writerow(['lang', 'topic', 'question', 'answer'])
                topics = faqs[faq]
                for topic in sorted(topics.keys()):
                    for row in topics[topic]:
                        writer.writerow([
                            row.locale, row.topic, row.question, row.answer])


class RowEntry(object):

    def __init__(self, locale, topic, question, answer):
        self.locale = locale
        self.topic = closest_ascii(topic)
        self.question = closest_ascii(question)
        self.answer = closest_ascii(answer)


def closest_ascii(s):
    """ Convert a Unicode string to ASCII by decomposing Unicode characters
        and then dropping the non-ASCII parts.
        """
    return unicodedata.normalize("NFKD", s).encode('ascii', errors='ignore')


def deep_merge_faqs(a, b):
    """ Merges FAQ dict b into dict a, combining sub-dictionaries as needed.
    """
    for k in b:
        b_v = b.get(k)
        a_v = a.get(k)
        if isinstance(a_v, dict) and isinstance(b_v, dict):
            deep_merge_faqs(a_v, b_v)
        elif isinstance(a_v, list) and isinstance(b_v, list):
            a_v.extend(b_v)
        elif a_v is None and isinstance(b_v, (dict, list)):
            a[k] = b_v
        else:
            raise ValueError("Unexpected FAQ values: %r, %r" % (a_v, b_v))


def main():
    input_files = sys.argv[1:]
    if not input_files:
        print ("Usage: %s src/refugee/fr.csv src/refugee/so.csv ..."
               % sys.argv[0])
        return 1

    converter = CsvConverter()
    all_faqs = {}
    categories = set()

    for input_file in input_files:
        category, csv_file = input_file.split(os.path.sep)[-2:]
        assert csv_file.endswith(".csv")
        locale = csv_file[:-len(".csv")]
        print "Parsing %ss (%s) ..." % (category, locale)
        categories.add(category)
        with open(input_file, "rb") as f:
            faqs = converter.parse(f, locale)
            deep_merge_faqs(all_faqs, faqs)

    if len(categories) != 1:
        print "Multiple categories (%r) given! Aborting." % (categories,)
        return 1

    converter.save(category, all_faqs)


if __name__ == "__main__":
    sys.exit(main())
