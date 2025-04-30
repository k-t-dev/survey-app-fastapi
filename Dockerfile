
#AWS
FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Step 7: Start FastAPI using uvicorn
CMD ["main.handler"]


#aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 536697225750.dkr.ecr.ap-northeast-1.amazonaws.com
#docker build -t survey-app/backend .
#docker tag survey-app/backend:latest 536697225750.dkr.ecr.ap-northeast-1.amazonaws.com/survey-app/backend:latest
#docker push 536697225750.dkr.ecr.ap-northeast-1.amazonaws.com/survey-app/backend:latest

#-----------------------------