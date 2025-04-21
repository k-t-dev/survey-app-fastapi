
import pandas as pd
import asyncpg
from src.crud import create_surevy_defs
import datetime
from src.logger_config import logger


async def preprocess_new_survey(shop_id, google_review_link, update_time, new_survey_dict):

    new_survey_df = pd.DataFrame()

    for survey in new_survey_dict:
        df = pd.DataFrame([
            {   'question_order': survey['question_order'],
                'question': survey['question'],
                'answer': answer_value,
                'first_question': survey['first_question'],
                'judge': survey['judge'][answer_id],
                'update_time': update_time,
                'google_review_link':google_review_link,
                'answer_order': answer_id,
            }
            for answer_id, answer_value in survey['answer'].items()
        ])

        new_survey_df = pd.concat([new_survey_df, df])

        new_survey_df['shop_id'] = shop_id
        # new_survey_df['update_time'] = pd.to_datetime(new_survey_df['update_time'], errors='coerce')

        print(new_survey_df['update_time'])
        print('~~~~~~~~~~~')

        #正規表現
        for key_col in (['question', 'answer']):
            new_survey_df[key_col] = new_survey_df[key_col].str.replace(" ", "").str.replace("　", "").str.replace("？", "").str.replace(r"[。！？]", "", regex=True)
        
    return new_survey_df


async def get_new_id(new_survey_df, defs_df, type="answer"):

    print(f'--->Type:{type}')

    new_defs_return_df = pd.DataFrame()

    key_dict = {
        "question":{"id_col":"question_id", "key_col": "question", "time_col":"question_registered_time", "table":"question_info"},
        "answer":{"id_col":"answer_id", "key_col": "answer", "time_col":"answer_registered_time", "table":"answer_info"},
        "google_link":{"id_col":"review_link_id", "key_col": "google_review_link", "time_col":"link_registered_time", "table":"review_link_info"}
    }

    key_col = key_dict[type]['key_col']
    id_col = key_dict[type]['id_col']
    time_col = key_dict[type]['time_col']
    table = key_dict[type]['table']

    #Get new columns list 
    df = new_survey_df[[key_col, 'update_time']].merge(defs_df, on=key_col, how='left').drop_duplicates()
    new_df = df[df[id_col].isna()][[key_col, 'update_time']]
    new_data = list(new_df.itertuples(index=False, name=None))

    print(new_data)

    #Insert Data to DB 
    if len(new_data) > 0:
        print(f'Go to create new defs:{new_df[key_col].to_list()}')
        new_defs_return_df = await create_surevy_defs(new_data, id_col, key_col, time_col, table)

    #Append for new id df and old is df
    all_defs_df = pd.concat([defs_df, new_defs_return_df])

    return all_defs_df


async def get_df_with_id(new_survey_df, question_all_defs_df, answer_all_defs_df, google_all_link_defs_df):

    new_survey_df = new_survey_df.merge(question_all_defs_df, on='question', how='left')
    new_survey_df = new_survey_df.merge(answer_all_defs_df, on='answer', how='left')
    final_df = new_survey_df.merge(google_all_link_defs_df, on='google_review_link', how='left')

    return final_df


async def devide_survey_data(new_survey, question_defs_df, answer_defs_df, google_link_defs_df, now):

    shop_id = new_survey.shop_id
    google_review_link = new_survey.google_review_link
    update_time = now
    new_survey_dict = new_survey.survey

    # Preprosess Survey Data
    new_survey_df = await preprocess_new_survey(shop_id, google_review_link, update_time, new_survey_dict)

    # print(question_defs_df)
    # print(answer_defs_df)
    # print(google_link_defs_df)

    # Get New Defs (Insert New Defs IDs and get the IDs)
    question_all_defs_df = await get_new_id(new_survey_df, question_defs_df, type="question") 
    answer_all_defs_df = await get_new_id(new_survey_df, answer_defs_df, type="answer")
    google_all_link_defs_df = await get_new_id(new_survey_df, google_link_defs_df, type="google_link")
    # Add Id to All Value
    final_new_survey_df = await get_df_with_id(new_survey_df, question_all_defs_df, answer_all_defs_df, google_all_link_defs_df)


    print('++++++++++')
    print(answer_all_defs_df)
    print(new_survey_df.columns)
    print(final_new_survey_df[['answer', 'answer_order']])
    print('++++++++++')
    
    return final_new_survey_df


async def preprocess_result_survey(survey_result):

    final_df = pd.DataFrame()

    shop_id = survey_result.shop_id
    user_id = survey_result.user_id
    answer_time = survey_result.answer_time
    survey_results_info = survey_result.results

    for survey in survey_results_info:
        df = pd.DataFrame([
            {
                'question_id': survey['question_id'],
                'answer_id': survey['answer_id'],
                'first_question': survey['first_question'],
                'judge': survey.get('judge', None)  # もしくは '' や False など適切なデフォルト値

            }
        ])
        final_df = pd.concat([final_df, df])

    final_df['shop_id'] = shop_id
    final_df['user_id'] = user_id
    final_df['answer_time'] = pd.to_datetime(answer_time)

    print(final_df)

    return final_df


async def preprocess_comment_result_survey(survey_result):

    final_df = pd.DataFrame()

    shop_id = survey_result.shop_id
    user_id = survey_result.user_id
    answer_time = survey_result.answer_time
    comment_page_results_info = survey_result.results

    for survey in comment_page_results_info:
        df = pd.DataFrame([
            {  
                'comment': survey['comment'],
                'star': survey['star'],
            }
        ])
        final_df = pd.concat([final_df, df])

    final_df['shop_id'] = shop_id
    final_df['user_id'] = user_id
    final_df['answer_time'] = pd.to_datetime(answer_time)

    return final_df



                      