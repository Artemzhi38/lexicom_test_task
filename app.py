import redis
import requests
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel


class FullData(BaseModel):
    phone: str
    address: str


class DataResponse(BaseModel):
    address: str


class SuggestionsResponse(BaseModel):
    suggestions: list


app = FastAPI()
address_storage = redis.Redis(host="redis", port=6379, decode_responses=True)


def ahunt_address_suggestions(addr: str):
    """Function that checks if address is real by using Ahunter API"""
    try:
        suggestions = requests.get(
            f"http://ahunter.ru/site/suggest/address?output=json;query={addr}"
        ).json()["suggestions"]
    except requests.exceptions.RequestException as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(err),
        )
    return [suggestion["value"] for suggestion in suggestions]


def phone_standard(phone: str):
    """Function that transforms phone number to 10-symbol string"""
    for symbol in "()-+ ":
        phone = phone.replace(symbol, "")
    if len(phone) == 11:
        return phone[1:]


@app.get("/check_data/{phone}")
def check_data(phone: str):
    """Endpoint for getting saved address by phone number"""
    phone_num = phone_standard(phone)
    address = address_storage.get(phone_num)
    if not address:
        return "No such phone in storage"
    return DataResponse(address=address)


@app.post("/write_data", status_code=status.HTTP_201_CREATED)
def add_new_data(data: FullData):
    """Endpoint for saving phone number and address data"""
    phone = phone_standard(data.phone)
    if phone and phone.isdigit() and len(phone) == 10:
        if data.address in ahunt_address_suggestions(data.address):
            address_storage.set(phone, data.address)
            return "Created"
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Address not validated",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone not validated",
        )


@app.patch("/write_data")
def update_data(data: FullData):
    """Endpoint for updating phone number and address data"""
    phone = phone_standard(data.phone)
    address = address_storage.get(phone)
    if address:
        if data.address in ahunt_address_suggestions(data.address):
            address_storage.set(phone, data.address)
            return "Updated"
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Address not validated",
            )
    else:
        return "No such phone in storage"


@app.get("/get_suggestions/{address}")
def get_suggestions(address: str):
    """Endpoint for getting right-formatted suggestions for address from
    Ahunter API"""
    suggestions = ahunt_address_suggestions(address)
    return SuggestionsResponse(suggestions=suggestions)
