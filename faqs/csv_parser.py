import csv


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
        topic_map = {
            "__current__": None
        }

        with open(self.filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter,
                                quotechar='"')
            for row in reader:
                self.handle_row(row, topic_map)

        return self

    def handle_row(self, row, topic_map):
        if len(row[0].strip()) > 0:
            new_topic = row[2].strip()
            topic_map[new_topic] = []
            topic_map["__current__"] = new_topic

        if row[4] == 'Back' or row[7] == 'Back' or len(row[7].strip()) == 0:
            return

        current_topic = topic_map["__current__"]
        assert current_topic is not None
        entry = RowEntry(self.locale, row[6], row[10], row[14])
        topic_map[current_topic].append(entry)
        return

    def save(self, destination_file):
        with open(destination_file, 'w') as output_file:
            output_file.write('locale,topic,question,answer\n')
            for topic in self.topic_map:
                for row in self.topic_map[topic]:
                    output_file.write("{0}\n".format(row.__str__()))


class RowEntry(object):

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
