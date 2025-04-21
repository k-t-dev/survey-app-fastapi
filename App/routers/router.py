from fastapi import HTTPException, status
from fastapi import APIRouter
from src import crud
from src import data_processing
from App.routers import schemas
import pandas as pd
from uuid import UUID
import time
from datetime import datetime

from src.logger_config import logger

router = APIRouter()

## TODO ##
"""
1 Create Endpoint 
2 Update UI for Graph
3 Apply those endpint to UI
4 Test in the Local
5 Get DNS 
6 Conider where is the アンケート running. (Lamda? Amplify? )
7 UI is run in the Amplify

*Consider UI
"""

#GET
@router.get("/companies", response_model=list[schemas.CompanyBase], summary="Get all companies")
async def get_companies():
    """Retrieve a list of all registered companies."""
    companies = await crud.get_company()  # Ensure async call
    return companies

@router.get("/shops", response_model=list[schemas.ShopBase], summary="Get all shops")
async def get_shops():
    """Retrieve a list of all registered shops."""
    shops = await crud.get_shop()  # Async call
    return shops

@router.get("/survey/{company_id}/{shop_id}", response_model=list[schemas.SurveyBase])
async def get_latest_survey(shop_id: str, company_id:str):
    """Retrieve the latest survey for a specific shop."""
    print("GET survey company_id",company_id)
    print("GET survey shop_id",shop_id)
    survey = await crud.get_latest_survey(shop_id, company_id)  # Async call
    return survey

@router.get("/survey-results/{company_id}/{shop_id}", response_model=list[schemas.SurveyResult])
async def get_survey_results(company_id:str, shop_id: str):
    """Retrieve the survey results for a specific shop."""
    print(f"GET SURVEY RESULT:{company_id}, {shop_id}")
    survey_results = await crud.get_survey_results(company_id, shop_id)  # Async call
    print('---------------')
    print(survey_results)
    print('---------------')
    return survey_results


############################################
#POST

#TODO NO-ALLOW Empty 
@router.post("/company", response_model=schemas.AddCompanyResponce, status_code=status.HTTP_201_CREATED, summary="Add a new company")
async def create_company(new_company: schemas.AddCompanyRequest):
    """Add a new company to the database."""
    now = datetime.now()
    return await crud.create_company(new_company, now)


@router.post("/shop/{shops_company_id}", response_model=schemas.AddShopResponse, status_code=status.HTTP_201_CREATED, summary="Add a new shop")
async def create_shop(shops_company_id:UUID, shop: schemas.AddShopRequest):

    print(shops_company_id)
    print(shop)
    now = datetime.now()
    """Add a new shop to the database."""
    return await crud.create_shop(shops_company_id, shop, now)  # Added await for async call

@router.post("/survey", response_model=schemas.Survey, summary="Add a new survey")
async def create_survey(new_survey: schemas.SurveyCreate):
    """Add a new survey to the database."""
    print(new_survey)
    question_defs_df, answer_defs_df, google_link_defs_df = await crud.get_surevy_defs()
    now = datetime.now()
    final_new_survey_df = await data_processing.devide_survey_data(new_survey, question_defs_df, answer_defs_df, google_link_defs_df, now)
    return await crud.create_survey(final_new_survey_df)

@router.post("/survey-results/general", response_model=schemas.Survey, summary="Add survey results")
async def create_survey_results(survey_result: schemas.NewSurveyResult):
    """Add survey results to the database."""
    final_new_survey_result_df = await data_processing.preprocess_result_survey(survey_result)
    return await crud.create_survey_result(final_new_survey_result_df)

@router.post("/survey-results/comment", response_model=schemas.Survey, summary="Add survey results")
async def create_comment_survey_results(survey_result: schemas.NewSurveyResult):
    """Add survey results to the database."""
    final_new_survey_result_df = await data_processing.preprocess_comment_result_survey(survey_result)
    return await crud.create_survey_comment_result(final_new_survey_result_df)


@router.post("/survey-link/{company_id}/{shop_id}", response_model=schemas.AddSurveyLinkResponce, status_code=status.HTTP_201_CREATED, summary="Add a new company")
async def create_survey_link(company_id:UUID, shop_id: UUID):
    """Add a new company to the database."""
    now = datetime.now()
    return await crud.create_survey_link(company_id, shop_id, now)

####################################################################

#UPDATE (only for shop and company)
@router.put("/company/{company_id}", response_model=schemas.BasicResponse, summary="Edit an existing company")
async def update_company(company_id: UUID, company: schemas.UpdateCompanyRequest):
    """Edit company details in the database."""
    print(f'UPDATE company:{company_id}')
    updated_company = await crud.update_company(company_id, company)
    return updated_company


@router.put("/shop/{company_id}/{shop_id}", response_model=schemas.BasicResponse, summary="Edit an existing shop")
async def update_company(company_id: UUID, shop_id: UUID, shop: schemas.ShopBasev2):
    """Edit company details in the database."""
    print(f'UPDATE Shop: {company_id}, {shop_id}')
    updated_company = await crud.update_shop(company_id, shop_id, shop)
    return updated_company


#Change company status
@router.put("/company/temp_status_changes/{company_id}/{contract}", response_model=schemas.BasicResponse, summary="Edit an existing company")
async def update_company(company_id: UUID, contract:str ):
    """Edit company details in the database."""
    print(f"!!CHANGE STATUS CONPANY!!-->> {company_id} | {contract}")
    now = datetime.now()
    updated_company = await crud.update_company_status(company_id, contract, now)
    return updated_company


#Change company status
@router.put("/shop/temp_status_changes/{company_id}/{shop_id}/{contract}", response_model=schemas.Response, summary="Edit an existing company")
async def update_company(company_id: UUID, shop_id:UUID, contract:str ):
    """Edit company details in the database."""
    print(f"!!CHANGE STATUS CONPANY!!--->>>> {company_id} | {shop_id} | {contract}")
    now = datetime.now()
    updated_company = await crud.update_shop_status(company_id, shop_id, contract, now)
    return updated_company


########################################################################################################################
#DELETE (only for shop and company) Cancel Date から１ヶ月以上で削除。

@router.delete("/company/{company_id}", response_model=schemas.BasicResponse, summary="Delete a company by ID")
async def delete_company(company_id: UUID):
    """Delete a company by its unique ID."""
    company = crud.delete_company(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )
    return company


@router.delete("/shop/{company_id}/{shop_id}", response_model=schemas.BasicResponse, summary="Delete a shop by ID")
def delete_shop(shop_id: UUID, company_id:UUID):
    """Delete a shop by its unique ID."""
    shop = crud.delete_shop(shop_id, company_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop with ID {shop_id} not found."
        )
    return shop
####################################################################



"""
契約日によっては表示と作動させない。
店舗情報で

"""