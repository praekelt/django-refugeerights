import csv
from django import forms
from .tasks import csv_importer
from .models import SnappyFaq, FailureLog


class CSVUploader(forms.Form):
    csv = forms.FileField()
    faq = forms.ModelChoiceField(queryset=SnappyFaq.objects.all())

    def is_valid(self):

        # run the parent validation first
        valid = super(CSVUploader, self).is_valid()

        # we're done now if not valid
        if not valid:
            return valid

        # so far so good, parse the CSV
        try:
            list(csv.DictReader(self.cleaned_data["csv"]))

        except csv.Error:
            self._errors['Upload Error'] = 'CSV could not be parsed!'
            # log file contents
            fl = FailureLog()
            fl.csv_content = self.cleaned_data["csv"]
            fl.save()
            return False

        # all good
        return True

    def save(self):
        csv_data = list(csv.DictReader(self.cleaned_data["csv"]))
        csv_importer.delay(csv_data, self.cleaned_data["faq"].snappy_id)
