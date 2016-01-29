import pandas as pd
import sqlalchemy as sql
from sys import argv

print('Parsing command line arguments...')
user, password = argv[1:]

print('Creating SQL engine...')
url = 'mysql://%s:%s@localhost/qa_365' %(user, password)
engine = sql.create_engine(url)

print('Reading Q text file...')
with open('Q_and_A_a_day.txt') as f:
    qs = f.readlines()
qs = [q.strip() for q in qs]

print('Inserting dates...')
dates = pd.date_range('2016-01-01', '2016-12-31')
df = {'month_': dates.month,
    'day_': dates.day,
    'question': qs,
    'question_id': list(range(366))
    }
df = pd.DataFrame(df)
df = df[['question_id', 'month_', 'day_', 'question']]

print('Inserting into MySQL...')
df.to_sql('questions', engine, index = False, if_exists = 'append')
print('Successfully inserted questions!')
