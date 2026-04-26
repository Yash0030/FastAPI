from fastapi import FastAPI,Path,HTTPException,Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
class patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of the patient', examples=['P001','P002'])]
    name:Annotated[str,Field(...,description='Name of the patient')]
    
    city:Annotated[str,Field(...,description='citu of the patient')]
    age:Annotated[int,Field(...,gt=0,lt=120,description='enter the age of the patient')]
    gender:Annotated[Literal['male','female','other'],Field(...,description='enter the gender of the patient')]
    
    height:Annotated[float,Field(...,gt=0,description='enter the height of the patient in mtrs')]
    weight:Annotated[float,Field(...,gt=0,description='enter the weigth of the patient in kgs')]
    @computed_field
    @property
    def bmi(self)-> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi<18.5:
            return 'underweight'
        elif self.bmi<25:
            return 'normal'
        elif self.bmi<30:
            return 'overweight'
        else: 
            return "obese"
    
class patient_update(BaseModel):
    
    name:Annotated[Optional[str],Field(default=None)]
    
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,gt=0)]
    gender:Annotated[Optional[Literal['male','female','other']],Field(default=None)]
    
    height:Annotated[Optional[float],Field(gt=0,default=None)]
    weight:Annotated[Optional[float],Field(gt=0,default=None)]
 
    
    
app=FastAPI()

@app.get("/")
def hello():
    return {'message':'Patient Management System API'}


@app.get('/about')
def about():
    return {'message':'A fully functional API to manage yout patient records'}

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
        
    return data

@app.get('/view')
def view():
    data=load_data()
    return data
#path param
@app.get('/patient/{patient_id}')
def view_patient(patient_id:str=Path(...,description='ID of the patient',example='P001')):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='Patient not found')
#query param
@app.get('/sort')
def sort_patient(sort_by:str=Query(...,description='Sort on the basis of height and weight'),order:str=Query('asc',description="sort in asc or desc order")):
    valid_fields=['height','weight','bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail='invalid field selct from {valid_fields}')
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='invalid order field')
    data=load_data()
    sort_order=True if order=='asc' else False
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    
    return sorted_data
    
def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)
    
@app.post('/create')
def creat_patient(patient:patient):
    data=load_data()
    if patient.id in data:
        raise HTTPException(status_code=400,detail='patient already exist')
    
    data[patient.id]=patient.model_dump(exclude=['id'])
    save_data(data)
    
    return JSONResponse(status_code=201,content={'message':'patient data is created'})
    
    
@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient_update:patient_update):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')
    
    existing_patient_info=data[patient_id]
    updated_patient_info=patient_update.model_dump(exclude_unset=True)
    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value
    
    existing_patient_info['id']=patient_id
    patient_pydantic_obj=patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_obj.model_dump(exclude='id')
    data[patient_id]=existing_patient_info
    save_data(data)
    
    return JSONResponse(status_code=200,content={'message':'patient updated'})
    
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')
    
    del data[patient_id]
    
    save_data(data)
    return JSONResponse(status_code=200,content={'message':'patient deleted'})
    
