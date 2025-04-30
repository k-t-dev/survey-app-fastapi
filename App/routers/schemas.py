from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from typing import Optional, List, Dict


#Done
class CompanyBase(BaseModel):
    company_id: UUID
    company_name: str
    company_address: str
    company_contact_address: str
    company_owner_name: str
    remarks: str


class ShopBase(BaseModel):
    shop_name: str
    shop_id: UUID
    company_id: UUID
    shop_owner_name: Optional[str] = None
    shop_contact_address: Optional[str] = None
    shop_location: Optional[str] = None
    start_contract_date: date = None
    end_contract_date: date = None
    shop_registered_time: datetime = None
    in_charge: Optional[str] = None
    remarks: Optional[str] = None
    company_name: Optional[str] = None
    survey_link: Optional[str] = None
    google_review_link: Optional[str] = None



class ShopBasev2(BaseModel):
    shop_name: str
    shop_owner_name: Optional[str] = None
    shop_contact_address: Optional[str] = None
    shop_location: Optional[str] = None
    start_contract_date: str = None
    end_contract_date: str = None
    shop_registered_time:str = None
    in_charge: Optional[str] = None
    remarks: Optional[str] = None


class SurveyBase(BaseModel):
    question: str
    answer: str
    shop_name: str
    shop_id: UUID
    question_id: UUID
    answer_id: UUID
    update_time: datetime
    first_question: bool
    judge: Optional[str]
    review_link_id:UUID
    google_review_link:str
    question_order:int
    answer_order:int


class SurveyResult(BaseModel):
    question: str
    answer: str
    shop_name: str
    shop_id: UUID
    question_id: UUID
    user_id: UUID
    answer_id: UUID
    answer_time: datetime
    first_question: bool
    judge: Optional[str]
    comment: Optional[str] = Field(default=None)
    star: Optional[int] = Field(default=None)

####################################

class AddCompanyRequest(BaseModel):
    company_name: str
    company_address: str
    company_contact_address: str
    company_owner_name: str
    remarks: str


class AddCompanyResponce(BaseModel):
    company_name: str
    company_id:UUID
    company_address: str
    company_contact_address: str
    company_owner_name: str
    remarks: str

class UpdateCompanyRequest(BaseModel):
    company_name: str
    company_address: str
    company_contact_address: str
    company_owner_name: str
    remarks: str
    contract: str


class UpdateCompanyStatusTempRequest(BaseModel):
    company_name: str
    contract: str

class AddShopRequest(BaseModel):
    shop_name: str
    shop_owner_name: Optional[str] = None
    shop_contact_address: Optional[str] = None
    shop_location: Optional[str] = None
    start_contract_date: Optional[str] = None
    end_contract_date: Optional[str] = None
    in_charge: Optional[str] = None
    remarks: Optional[str] = None

class AddShopResponse(BaseModel):
    shop_name: str
    company_id:UUID
    shop_id:UUID
    shop_owner_name: Optional[str] = None
    shop_contact_address: Optional[str] = None
    shop_location: Optional[str] = None
    start_contract_date: Optional[date] = None
    end_contract_date: Optional[date] = None
    in_charge: Optional[str] = None
    remarks: Optional[str] = None


class AddShopResponce(BaseModel):

    status: str
    new_shop: str

class Response(BaseModel):
    status: str
    message: str


class SurveyItem(BaseModel):
    question: str
    answer: Dict[str, str]
    first_question: bool
    judge: Dict[str, str]
    update_time: str  # Consider using `datetime` if this should be a date

class SurveyCreate(BaseModel):
    shop_id: str
    google_review_link: str
    survey: List[Dict]  # Use a structured model instead of `List[Dict]`

class NewSurveyResult(BaseModel):
    shop_id: UUID
    user_id: UUID
    answer_time:Optional[str]
    results: List[Dict]  # Use a structured model instead of `List[Dict]`




####################################
# # survey: List[Dict] = Field(..., description="")
# #Set conditions for requesting body
# unique_alarm_id_list: List[str] = Field(...,)
# required_alarm_ids: List[str] = Field(...,)
# pics_dict: Dict = Field(..., description="")
# mcdr_session_dict: Dict = Field(..., description="")
# all_rca_payload: Dict = Field(..., description="")
# recipient: List[str] = Field(...,)


class Survey(BaseModel):
    status: str

    class Config:
        status = ''  # ✅ これが正しい
        
class AddSurveyLinkResponce(BaseModel):
    company_id:UUID
    shop_id: UUID
    survey_link: str
        

class BasicResponse(BaseModel):
    status: str

    class Config:
        status = ''  # ✅ これが正しい


class Company(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ShopCreate(ShopBase):
    pass
