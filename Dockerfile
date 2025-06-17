# Use a imagem oficial Python como base
FROM public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY src/app.py ${LAMBDA_TASK_ROOT}

# Copy model file
COPY model/model.pkl ${LAMBDA_TASK_ROOT}/model/

# Copy version file
COPY model/model_metadata.json ${LAMBDA_TASK_ROOT}/model

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]