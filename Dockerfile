FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy all the project files into the task root
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD ["api.index.handler"]
