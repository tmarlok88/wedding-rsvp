import csv
import io
from app.model.Guest import Guest


class CSVHandler:

    @staticmethod
    def import_csv(data: str) -> bool:
        reader = csv.DictReader(io.StringIO(data), delimiter=',', quotechar='"')
        with Guest.batch_write():
            for row in reader:
                guest = Guest(**row)
                guest.save()
            return True

    @staticmethod
    def export_csv() -> io.StringIO:
        guest_list = Guest.scan()
        outputfile = io.StringIO()
        fields = Guest.get_attributes().keys()
        writer = csv.DictWriter(outputfile, fieldnames=fields, delimiter=',', quotechar='"')
        writer.writeheader()
        for guest in guest_list:
            writer.writerow(guest.attribute_values)
        return outputfile
