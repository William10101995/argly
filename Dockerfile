FROM public.ecr.aws/lambda/python:3.12

RUN dnf update -y && dnf clean all

# Copy requirements.txt and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# aws-lambda-rie es solo para testing local (RIE emulator), no se usa en producción.
# Se elimina para evitar que sus CVEs de Go stdlib bloqueen el Trivy gate.
RUN rm -f /usr/local/bin/aws-lambda-rie

# Copy all the project files into the task root
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD ["api.index.handler"]