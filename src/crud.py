from src.database import db
import time
import pandas as pd
import asyncpg
import asyncio
import traceback
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime

from src.logger_config import logger

#GET
async def get_company():
    # Acquire a connection
    conn = await db.get_connection()
    try:
        # Run the query inside the connection context
        query = """
            SELECT
                "company_id",
                "company_name",
                "company_address",
                "company_owner_name",
                "company_contact_address",
                "remarks"
            FROM company_info
            where "contract" = 'contract'
        """
        df = await conn.fetch(query)  # Use `fetch` for async queries
        return [dict(record) for record in df]
    finally:
        # Release the connection back to the pool
        await db.pool.release(conn)


async def get_shop():
    conn = await db.get_connection()
    try:
        # query = """
        # SELECT
        #     shop_info.*,
        #     company_name
        # FROM shop_info
        # LEFT JOIN company_info ON company_info.company_id = shop_info.company_id
        # Where company_info."contract" = 'contract' and shop_info."contract" = 'contract'
        # """
        
        query ="""
            WITH latest_google_link_info_tb as (
                SELECT DISTINCT ON (set_survey_tb.shop_id)
                    set_survey_tb.shop_id,
                    google_review_link
                FROM latest_question_answer_comb set_survey_tb
                left join review_link_info on review_link_info.review_link_id = set_survey_tb.review_link_id
                ORDER BY set_survey_tb.shop_id, set_survey_tb.update_time DESC
            )
            SELECT
                company_info.company_name,
                shop_info.*,
                survey_link_info.survey_link,
                latest_google_link_info_tb.google_review_link
            FROM shop_info 
            LEFT JOIN company_info ON company_info.company_id = shop_info.company_id
            LEFT JOIN survey_link_info ON survey_link_info.shop_id = shop_info.shop_id
            LEFT JOIN latest_google_link_info_tb ON latest_google_link_info_tb.shop_id = shop_info.shop_id
            Where company_info."contract" = 'contract' and shop_info."contract" = 'contract';
        """
        df = await conn.fetch(query)  # Use `fetch` for async queries

        return [dict(record) for record in df]
    
    finally:
        # Release the connection back to the pool
        await db.pool.release(conn)

#TODO 
async def get_latest_survey(shop_id: str, company_id:str):
    conn = await db.get_connection()
    try:
        query=f"""
            with base as (
            SELECT
                tb.*,
                company_info.contract as company_contract,
                shop_info.contract as shop_contract,
                shop_info.shop_name
                FROM latest_question_answer_comb tb
                left join shop_info on shop_info.shop_id = tb.shop_id
                LEFT JOIN company_info on company_info.company_id = shop_info.company_id
                WHERE tb.shop_id = '{shop_id}' and company_info.company_id = '{company_id}'
            AND update_time = (SELECT MAX(update_time) FROM latest_question_answer_comb WHERE shop_id = '{shop_id}')
            )
            SELECT
                question_info.question,
                answer_info.answer,
                base.shop_name,
                review_link_info.google_review_link,
                base.shop_id,
                base.question_id,
                base.answer_id,
                base.first_question,
                base.judge,
                base.update_time,
                base.review_link_id,
                base.question_order,
                base.answer_order
            from base
            left join question_info on question_info.question_id = base.question_id
            left join answer_info on answer_info.answer_id = base.answer_id
            left join review_link_info on review_link_info.review_link_id = base.review_link_id
            Where "shop_contract" = 'contract' and "company_contract" = 'contract' 
        """
        latest_registred_suvey_data = await conn.fetch(query)  # Use `fetch` for async queries

        print('!!!!!!!!!!!!')
        print(latest_registred_suvey_data)
        print('!!!!!!!!!!!!')
        return [dict(record) for record in latest_registred_suvey_data]
    
    finally:
        # Release the connection back to the pool
        await db.pool.release(conn)

async def get_surevy_defs():
    conn = await db.get_connection()
    try:
        query=f"""
            select 
            question_id, 
            question 
            from question_info
        """
        question_defs = await conn.fetch(query)  # Use `fetch` for async queries

        query=f"""
            select 
            answer_id, 
            answer
            from answer_info
        """
        answer_defs = await conn.fetch(query)  # Use `fetch` for async queries

        query=f"""
            select 
            review_link_id, 
            google_review_link
            from review_link_info
        """
        google_link_defs = await conn.fetch(query)  # Use `fetch` for async queries

        question_defs_df = pd.DataFrame(question_defs, columns=["question_id", "question"])
        answer_defs_df = pd.DataFrame(answer_defs, columns=["answer_id", "answer"])
        google_link_defs_df = pd.DataFrame(google_link_defs, columns=["review_link_id", "google_review_link"])
        
        return question_defs_df, answer_defs_df, google_link_defs_df
    
    finally:
        # Release the connection back to the pool
        await db.pool.release(conn)


async def get_survey_results(company_id: str, shop_id: str,):
    conn = await db.get_connection()
    try:
    
        query=f"""
            SELECT
                question_info.question,
                answer_info.answer,
                shop_info.shop_name,
                commnet_answer_result_table."comment",
                commnet_answer_result_table."star",
                tb.*
            from answer_result_table tb
            left join question_info on question_info.question_id = tb.question_id
            left join answer_info on answer_info.answer_id = tb.answer_id
            left join shop_info on shop_info.shop_id = tb.shop_id
            left join company_info on company_info.company_id = shop_info.company_id
            left join commnet_answer_result_table on commnet_answer_result_table.shop_id = tb.shop_id and commnet_answer_result_table.user_id = tb.user_id
            WHERE tb.shop_id = '{shop_id}' and company_info.company_id = '{company_id}'
            AND shop_info."contract" = 'contract' and company_info."contract" = 'contract' 
        """
        df = await conn.fetch(query)  # Use `fetch` for async queries

        return [dict(record) for record in df]
    
    finally:
        # Release the connection back to the pool
        await db.pool.release(conn)


##########################################################################

#POST
#-------
async def create_company(new_company, now):

    conn = await db.get_connection()

    query = """
    INSERT INTO company_info (company_name, company_address, company_contact_address, company_owner_name, remarks, contract, company_register_time)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING company_name, company_id ,company_address, company_contact_address, company_owner_name, remarks;
    """

    try:
        added_company = await conn.fetchrow(
            query,
            new_company.company_name,
            new_company.company_address,
            new_company.company_contact_address,
            new_company.company_owner_name,
            new_company.remarks,
            "contract",
            now
            
        )
        return dict(added_company)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Company already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

async def create_shop(company_id, new_shop, now):

    conn = await db.get_connection()

    new_shop.start_contract_date = datetime.strptime(new_shop.start_contract_date, "%Y-%m-%d").date()
    new_shop.end_contract_date = datetime.strptime(new_shop.end_contract_date, "%Y-%m-%d").date()

    query = """
    INSERT INTO shop_info (shop_name, company_id, shop_owner_name, shop_contact_address, shop_location, start_contract_date, end_contract_date, shop_registered_time, in_charge, remarks, contract
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    RETURNING  shop_name, company_id, shop_id, shop_owner_name, shop_contact_address, shop_location, start_contract_date, end_contract_date, in_charge, remarks;
    """

    try:
        added_shop = await conn.fetchrow(
            query,
            new_shop.shop_name,
            company_id,
            new_shop.shop_owner_name,
            new_shop.shop_contact_address,
            new_shop.shop_location,
            new_shop.start_contract_date,
            new_shop.end_contract_date,
            now,
            new_shop.in_charge,
            new_shop.remarks,
            "contract"
        )

        # if update_company:
        #     return {"status": "success", "message": str(new_shop.shop_name)}
        # else:
        #     return {"status": "failed", "message": "shop not saved"}
        return dict(added_shop)

    except asyncpg.exceptions.UniqueViolationError:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Shop already exists")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


async def create_surevy_defs(new_data, id_col, key_col, time_col, table):
    conn = await db.get_connection()
    try:
        # 動的に $1, $2, ... を生成
        values_clause = ','.join(
            f'(${i*2+1}, ${i*2+2})' for i in range(len(new_data))
        )
        # 平坦な list に展開
        args = [val for tup in new_data for val in tup]

        query = f"""
            INSERT INTO {table} ({key_col}, {time_col})
            VALUES {values_clause}
            RETURNING {id_col}, {key_col};
        """
        new_defs_return = await conn.fetch(query, *args)

        new_defs_return_df = pd.DataFrame(new_defs_return, columns=[id_col, key_col])
        
        return new_defs_return_df
    
    finally:
        # Release the connection back to the pool
        await db.pool.release(conn)


async def create_survey(final_new_survey_df):

    conn = await db.get_connection()

    query = """
        INSERT INTO latest_question_answer_comb (shop_id, question_id, answer_id, update_time, first_question, judge, review_link_id, question_order, answer_order)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING shop_id, question_id, answer_id
    """
    try:
        # 'update_time' を datetime 型に変換
        final_new_survey_df['update_time'] = pd.to_datetime(final_new_survey_df['update_time'], errors='coerce')
        final_new_survey_df['update_time'] = final_new_survey_df['update_time'].dt.to_pydatetime()
        
        # DataFrameをリスト形式に変換
        values = [
            (row.shop_id, row.question_id, row.answer_id, row.update_time, row.first_question, row.judge, row.review_link_id, row.question_order, int(row.answer_order))
            for row in final_new_survey_df.itertuples(index=False)
        ]
        print(values)
        # 複数行を一括挿入
        added_surveys = await conn.executemany(query, values)

        return {"status": "success"}
    except asyncpg.exceptions.UniqueViolationError:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Survey already exists")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


async def create_survey_result(final_new_survey_result_df):
    print(final_new_survey_result_df.columns)
    conn = await db.get_connection()
    query = """
    INSERT INTO answer_result_table (shop_id, question_id, answer_id, user_id, answer_time, first_question, judge)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING shop_id, question_id, answer_id;
    """
    try:
        # DataFrameをリスト形式に変換
        values = [
            (row.shop_id, row.question_id, row.answer_id, row.user_id, row.answer_time, row.first_question, row.judge)
            for row in final_new_survey_result_df.itertuples(index=False)
        ]

        # 複数行を一括挿入
        added_surveys = await conn.executemany(query, values)

        # # 結果を辞書形式に変換
        # result = [dict(row) for row in added_surveys]
        return {"status": "success"}
        # return dict(added_surveys)

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Survey already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()



async def create_survey_comment_result(final_new_survey_result_df):

    conn = await db.get_connection()

    query = """
    INSERT INTO commnet_answer_result_table (shop_id, user_id, answer_time, comment, star)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING shop_id, user_id;
    """
    try:
        # DataFrameをリスト形式に変換
        values = [
            (row.shop_id,  row.user_id, row.answer_time, row.comment, row.star)
            for row in final_new_survey_result_df.itertuples(index=False)
        ]

        # 複数行を一括挿入
        added_surveys = await conn.executemany(query, values)

        logger.info("FINISH: Insert Data to commnet_answer_result_table")
        # return dict(added_surveys)
        return {"status": "success"}
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Survey already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()
        
        
async def create_survey_link(company_id, shop_id, now):
    
    survey_link = f'https://review.com/survey/{company_id}/{shop_id}'
    conn = await db.get_connection()

    query = """
    INSERT INTO survey_link_info (company_id, shop_id, survey_link, created_time)
    VALUES ($1, $2, $3, $4)
    RETURNING company_id, shop_id, survey_link;
    """

    try:
        values = [company_id, shop_id, survey_link, now]
        added_survey = await conn.fetchrow(query, *values)
        logger.info("FINISH: Insert Data to survey_link_info")
        return dict(added_survey)
    
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Survey already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


############################################################

#PUT
async def update_company(company_id: UUID, company: dict):
    # PostgreSQLへ非同期接続
    conn = await db.get_connection()

    company = dict(company)
    company.update({'company_id':company_id})
    df = pd.DataFrame([company])
 
    try:
        
        query="""UPDATE company_info
            SET 
                company_name = $2,
                company_address = $3,
                company_owner_name = $4,
                company_contact_address = $5,
                remarks = $6,
                contract = $7
            WHERE company_id = $1
            RETURNING company_id
        """
        
        values = [
            (row.company_id,  row.company_name, row.company_address, row.company_owner_name, row.company_contact_address, row.remarks, row.contract)
            for row in df.itertuples(index=False)
        ]
        # 複数行を一括挿入
        added_surveys = await conn.executemany(query, values)
        
        # 成功時には更新された会社情報を返す
        return {"status": "success"}
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        await conn.close()

async def update_shop(company_id: UUID, shop_id: UUID, shop:dict):
    # PostgreSQLへ非同期接続
    conn = await db.get_connection()

    shop = dict(shop)
    shop.update({'shop_id':shop_id, 'company_id':company_id})
    df = pd.DataFrame([shop])

    try:
        query="""UPDATE shop_info
                SET 
                    shop_name = $3,
                    shop_owner_name = $4,
                    shop_contact_address = $5,
                    shop_location = $6,
                    start_contract_date = $7,
                    end_contract_date = $8,
                    in_charge = $9,
                    remarks = $10
                WHERE shop_id = $1 AND company_id = $2
                RETURNING shop_id;
        """
        
        values = [
            (
                row.shop_id, 
                row.company_id, 
                row.shop_name, 
                row.shop_owner_name,
                row.shop_contact_address, 
                row.shop_location,
                datetime.strptime(row.start_contract_date, "%Y-%m-%d") if isinstance(row.start_contract_date, str) else row.start_contract_date,
                datetime.strptime(row.end_contract_date, "%Y-%m-%d") if isinstance(row.end_contract_date, str) else row.end_contract_date,
                row.in_charge, 
                row.remarks,
            )
            for _, row in df.iterrows()
        ]

        # 複数行を一括挿入
        added_surveys = await conn.executemany(query, values)

        print('added_surveys', added_surveys)
        
        # 成功時には更新された会社情報を返す
        return {"status": "success"}
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        await conn.close()


async def update_company_status(company_id: UUID, contract: str, now: time):
    # PostgreSQLへ非同期接続
    conn = await db.get_connection()
 
    try:
        
        query="""UPDATE company_info
            SET 
                contract = $2,
                company_change_status_time = $3

            WHERE company_id = $1
            RETURNING company_id
        """
        values = [company_id, contract, now]
        update_company = await conn.fetchrow(query, *values)
        
        if update_company:
            return {"status": "success", "deleted_company_id": str(update_company)}
        else:
            return {"status": "failed", "message": "Company not found"}
        
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        await conn.close()


async def update_shop_status(company_id: UUID, shop_id:UUID, contract: str, now: time):
    # PostgreSQLへ非同期接続
    conn = await db.get_connection()
 
    try:
        
        query="""UPDATE shop_info
            SET 
                contract = $3,
                shop_change_status_time = $4
            WHERE company_id = $1 and shop_id = $2
            RETURNING company_id, shop_id
        """
        values = [company_id, shop_id, contract, now]
        update_company = await conn.fetchrow(query, *values)

        print(f'!!!!!!!!!!!!!!!!:{update_company}')
        
        if update_company:
            return {"status": "success", "message": f"Delete shop: {str(shop_id)}"}
        else:
            return {"status": "failed", "message": "Company not found"}
        
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        await conn.close()

##########################################################

# DELETE
async def delete_company(company_id: UUID):
    # PostgreSQLへ非同期接続
    conn = await db.get_connection()

    try:
        query = """DELETE FROM company_info 
                   WHERE company_id = $1
                   RETURNING company_id;"""
        
        values = (company_id)

        deleted_company = await conn.fetchval(query, *values)

        if deleted_company:
            return {"status": "success", "deleted_company_id": str(deleted_company)}
        else:
            return {"status": "failed", "message": "Company not found"}
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        await conn.close()



async def delete_shop(company_id: UUID, shop_id: UUID):
    # PostgreSQLへ非同期接続
    conn = await db.get_connection()

    try:
        query = """DELETE FROM shop_info 
                   WHERE shop_id = $1 AND company_id = $2 
                   RETURNING shop_id;"""
        
        values = (shop_id, company_id)

        deleted_shop = await conn.fetchval(query, *values)

        if deleted_shop:
            return {"status": "success", "deleted_shop_id": str(deleted_shop)}
        else:
            return {"status": "failed", "message": "Shop not found"}
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        await conn.close()



