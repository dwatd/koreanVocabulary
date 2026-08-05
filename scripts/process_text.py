import re
import sys
import pandas as pd
from pandas import DataFrame
from konlpy.tag import Okt
from collections import Counter
from deep_translator import MyMemoryTranslator

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
# text = """한강은 서울 도심을 지나가는 강입니다. 옛날 사람들은 한강 물을 마시고 한강에서 낚시도 하면서 살았습니다. 그리고 기차나 차가 없을 때 한강에서 배를 타고 다른 지역으로 갔습니다. 긴 역사 속에서 한강은 한국 사람들에게 중요한 강이었습니다."""
text = sys.stdin.read()
text = re.sub(r'[^\w\s]', '', text)

okt = Okt()
tokens = okt.pos(text, norm=True, stem=True)

# Preprocessing
filtered_tokens = []
for word, pos in tokens:
  if pos == 'Noun' or pos == 'Verb' or pos == 'Adjective':
    filtered_tokens.append(word)

counted_tokens = Counter(filtered_tokens)
my_words_df = DataFrame.from_records(data=counted_tokens.most_common(), columns=['word', 'frequency'])

# TOPIK words list
df_topik = pd.read_csv('results.tsv', sep='\t')

df_topik['word'] = df_topik['word'].str.replace(r'\d+', '', regex=True)
df_topik = df_topik.drop_duplicates(subset=['word'])

# Merge data
final_df = pd.merge(my_words_df, df_topik, on='word', how='left').drop(columns=['rank', 'hanja', 'explanation', 'nikl_level'])
final_df = final_df.fillna({'topik_level': 'Not in the dictionary', 'part_of_speech': 'Unknown'})

# Translation
translator = MyMemoryTranslator(source='korean', target='english')

def safe_translate(text):
    if pd.isna(text):
        return text

    try:
        clean_text = str(text).strip()
        return translator.translate(clean_text)
    except Exception as e:
        return f"[Помилка: {e}]"

final_df['translation'] = final_df['word'].apply(safe_translate)

json_result = final_df.to_json(orient='records', force_ascii=False)
print(json_result)