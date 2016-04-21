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
        for row in reader:
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

        new_topic = row[2].strip()
        if new_topic and new_topic != current_topic:
            current_topic = faqs["__current_topic__"] = new_topic
            faq[current_topic] = []
            return
        topic = faq[current_topic]

        if row[4] == 'Back' or row[7] == 'Back' or len(row[7].strip()) == 0:
            return

        entry = RowEntry(
            locale, self._decode(row[6]), self._decode(row[10]),
            self._decode(row[15]))
        topic.append(entry)
        return

    def save(self, refugee_type, locale, faqs):
        for faq in sorted(faqs.keys()):
            output_file = os.path.join(refugee_type, locale, "%s.csv" % faq)
            with open(output_file, "wb") as f:
                writer = csv.writer(f)
                writer.writerow(['locale', 'topic', 'question', 'answer'])
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


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: %s <refugee-or-migrant> <locale>" % sys.argv[0])
        return 1
    [refugee_type, locale] = sys.argv[1:]
    converter = CsvConverter()
    input_file = os.path.join("src", refugee_type, "%s.csv" % locale)
    with open(input_file, "rb") as f:
        faqs = converter.parse(f, locale)
    converter.save(refugee_type, locale, faqs)


if __name__ == "__main__":
    sys.exit(main())
