import csv
import unicodedata


class CsvContentParser(object):

    def __init__(self, filename, locale, delimiter):
        if len(filename) < 1:
            raise RuntimeError("Filename cannot be blank")

        if len(locale) != 2:
            raise RuntimeError("Locale must have a length of 2")

        if len(delimiter) != 1:
            raise RuntimeError("delimiter must have a length of 1")

        self.filename = filename
        self.locale = locale
        self.delimiter = delimiter

    def parse(self):
        topics = {
            "__current__": None
        }

        with open(self.filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter,
                                quotechar='"')
            for row in reader:
                self.handle_row(row, topics)

        del topics["__current__"]
        return topics

    def handle_row(self, row, topics):
        if len(row[0].strip()) > 0:
            new_topic = row[2].strip()
            topics[new_topic] = []
            topics["__current__"] = new_topic

        if row[4] == 'Back' or row[7] == 'Back' or len(row[7].strip()) == 0:
            return

        current_topic = topics["__current__"]
        entry = RowEntry(self.locale, row[6], row[10], row[14])
        topics[current_topic].append(entry)
        return

    def save(self, destination_file, topics):
        with open(destination_file, 'w') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(['locale', 'topic', 'question', 'answer'])
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
    csv_parser = CsvContentParser('migrant-content.csv', 'so', ',')
    topics = csv_parser.parse()
    csv_parser.save('output-migrant-content.csv', topics)


if __name__ == "__main__":
    main()
