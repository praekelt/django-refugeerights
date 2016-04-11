import csv


class CsvContentParser(object):
    filename = ""
    locale = ""
    topic_map = {}
    current_topic = ""
    delimiter = ''

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
        with open(self.filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter,
                                quotechar='"')
            for row in reader:
                self.handle_row(row)

        return self

    def handle_row(self, row):
        if len(row[0].strip()) > 0:
            self.current_topic = row[2].strip()
            self.topic_map[self.current_topic] = []
            return

        if row[4] == 'Back' or row[7] == 'Back' or len(row[7].strip()) == 0:
            return

        entry = RowEntry(self.locale, row[6], row[10], row[14])

        self.topic_map[self.current_topic].append(entry)

    def save(self, destination_file):
        with open(destination_file, 'w') as output_file:
            output_file.write('locale,topic,question,answer\n')
            for topic in self.topic_map:
                for row in self.topic_map[topic]:
                    output_file.write("{0}\n".format(row.__str__()))


class RowEntry(object):
    locale = ""
    topic = ""
    question = ""
    answer = ""

    def __init__(self, locale, topic, question, answer):
        self.locale = self.escape_string(locale)

        self.topic = self.escape_string(topic)
        self.question = self.escape_string(question)
        self.answer = self.escape_string(answer)

    def __str__(self):
        return "{0},{1},{2},{3}".format(self.locale, self.topic, self.question,
                                        self.answer)

    def escape_string(self, text, delimiter=',', force=False):
        if (delimiter in text) or force:
            return '"{0}"'.format(text)
        else:
            return text


def main():
    CsvContentParser('migrant-content.csv', 'so', ',').parse().save(
        'output-migrant-content.csv')


if __name__ == "__main__":
    main()
