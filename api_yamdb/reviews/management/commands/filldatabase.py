import csv
import os
import sqlite3

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    @staticmethod
    def filter_files(path, endswith):
        result = []
        for root, _, files in os.walk(path):
            for name in files:
                if name.endswith(endswith):
                    result.append(os.path.join(root, name))
        return result

    def handle(self, *args, **options):
        app_name = 'reviews'

        db_folder = os.getcwd()
        db_name = 'db.sqlite3'
        csv_folder = os.path.join(db_folder, 'static', 'data')

        db_file = os.path.join(db_folder, db_name)
        csv_files = self.filter_files(csv_folder, endswith='.csv')

        con = sqlite3.connect(db_file)
        cur = con.cursor()

        for csv_file in csv_files:
            with open(csv_file, 'r', encoding='utf-8') as f:
                dr = csv.DictReader(f)

                table_name, _ = os.path.basename(csv_file).split('.')
                full_table_name = f'{app_name}_{table_name}'

                fieldnames_string = ', '.join(dr.fieldnames)
                questions_string = ', '.join(['?'] * len(dr.fieldnames))

                data = [tuple(row.values()) for row in dr]

                try:
                    sql_request = (
                        "INSERT INTO {}({}) VALUES ({});".format(
                            full_table_name,
                            fieldnames_string,
                            questions_string
                        )
                    )
                    cur.executemany(sql_request, data)
                    msg = 'Таблица {} успешно заполнена!'.format(
                        full_table_name
                    )

                except sqlite3.IntegrityError:
                    msg = 'Таблица {} уже заполнена!'.format(full_table_name)

                except sqlite3.OperationalError:
                    sql_request = (
                        "CREATE TABLE {}({})".format(
                            full_table_name,
                            fieldnames_string
                        )
                    )
                    cur.execute(sql_request)
                    msg = 'Таблица {} создана.'.format(full_table_name)

                self.stdout.write(self.style.SUCCESS(msg))
                con.commit()
        con.close()
