FROM public.ecr.aws/lambda/python:3.10

COPY detect_idle_lambdas.py ${LAMBDA_TASK_ROOT}

CMD [ "detect_idle_lambdas.lambda_handler" ]
