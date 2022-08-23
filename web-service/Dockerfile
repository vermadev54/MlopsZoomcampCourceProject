FROM public.ecr.aws/lambda/python:3.9

RUN pip install -U pip
RUN pip install pipenv 
RUN pip install requests

WORKDIR /app

COPY [ "/Pipfile", "/Pipfile.lock", "./" ]

RUN pipenv install --system --deploy



COPY [ "predict.py", "./" ]

EXPOSE 8001

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:8001", "predict:app" ]