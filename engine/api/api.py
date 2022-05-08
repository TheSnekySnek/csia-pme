import os
import yaml
import pydantic
import io
import json
import datetime

from inspect import Parameter, Signature
from typing import Union, List
from fastapi import FastAPI, HTTPException, UploadFile, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .Engine import Engine, Registry, Cron, Enums
from . import interface

def addRoute(route, body, summary=None, description=None):
	# This should be wrapped in a functor, howevera bug in starlette prevents the handler to be correctly called if __call__ is declared async. This should be fixed in version 0.21.0 (https://github.com/encode/starlette/pull/1444).
	async def handler(*args, **kwargs):
		jobData = {}
		binaries = []
		
		if type(body) is dict:
			jobData.update(kwargs["data"].dict())
		elif type(body) is str:
			binaries.append(body)
		elif type(body) is list:
			binaries = body
		
		if len(binaries) > 0:
			request = kwargs["req"]
			form = await request.form()
			for name in binaries:
				obj = form[name]
				if obj.content_type == "application/json":
					payload = await obj.read()
					jobData.update(json.loads(payload))
				else:
					jobData[name] = obj

		jobId = await engine.newJob(route, jobData, binaries)
		return {"jobId": jobId}
	
	# Change the function signature with expected types from the api description so that the api doc is correctly generated
	params = []
	if type(body) is dict:
		model = pydantic.create_model(route + "Body", **body)
		params.append(Parameter("data", kind=Parameter.POSITIONAL_ONLY, annotation=model))
	elif type(body) is str:
		params.append(Parameter(body, kind=Parameter.POSITIONAL_ONLY, annotation=UploadFile))
	elif type(body) is list:
		for name in body:
			params.append(Parameter(name, kind=Parameter.POSITIONAL_ONLY, annotation=UploadFile))
	params.append(Parameter("req", kind=Parameter.POSITIONAL_ONLY, annotation=Request))
	handler.__signature__ = Signature(params)

	app.add_api_route("/services/" + route, handler, methods=["POST"],  response_model=interface.JobResponse, summary=summary, description=description)
	# Force the regeneration of the schema
	app.openapi_schema = None

async def startup():
	global registry
	global engine
	global timer

	registry = await Registry.Registry.create(
		s3_url=os.environ["S3_URL"] if "S3_URL" in os.environ else None,
		s3_zone=os.environ["S3_ZONE"] if "S3_ZONE" in os.environ else None,
		s3_key=os.environ["S3_KEY_ID"] if "S3_KEY_ID" in os.environ else None,
		s3_secret=os.environ["S3_SECRET_KEY"] if "S3_SECRET_KEY" in os.environ else None,
		s3_bucket=os.environ["S3_BUCKET"] if "S3_BUCKET" in os.environ else None,
		binFolder=os.environ["REG_LOCAL_DATA"] if "REG_LOCAL_DATA" in os.environ else None,
		storageType=os.environ["REG_STORAGE_TYPE"] if "REG_STORAGE_TYPE" in os.environ else Enums.StorageType.LOCAL,
		mongo_uri=os.environ["MONGO_URI"] if "MONGO_URI" in os.environ else None,
		mongo_db=os.environ["MONGO_DB"] if "MONGO_DB" in os.environ else None,
		dbType=os.environ["REG_DB_TYPE"] if "REG_DB_TYPE" in os.environ else Enums.DBType.MEMORY)
	
	engine = Engine.Engine(
		registry=registry,
		route=os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None,
		externalRoute=os.environ["APP_EXTERNAL_URL"] if "APP_EXTERNAL_URL" in os.environ else None)
	
	# To refactor?
	await engine.load()
	engine.start()
	
	tick = int(os.environ["APP_CRON"]) if "APP_CRON" in os.environ else 300
	lifespan = int(os.environ["APP_LIFESPAN"]) if "APP_LIFESPAN" in os.environ else 1800
	engineCleanTimer = Cron.Timer(
		timeout=tick,
		callback=engine.clean,
		delta=datetime.timedelta(seconds=lifespan))
	engineCleanTimer.start()
	timers.append(engineCleanTimer)

	s3CleanTimer = Cron.Timer(
		timeout=20*tick,
		callback=registry.clean,
		delta=datetime.timedelta(seconds=10*lifespan))
	s3CleanTimer.start()
	timers.append(s3CleanTimer)

async def shutdown():
	await engine.stop()
	for timer in timers:
		timer.stop()

app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])
registry = None
engine = None
timers = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tasks/{taskId}", summary="Get results of a task")
async def getTaskResult(taskId: str):
	result = await engine.getResult(taskId)
	return JSONResponse(result)

@app.get("/tasks/{taskId}/status", summary="Get the status of a task")
async def getTaskStatus(taskId: str):
	return await engine.pollTask(taskId)

@app.get("/tasks/{taskId}/raw", summary="Get raw pipeline data for a task")
async def getTaskRaw(taskId: str):
	raw = await engine.getJobRaw(taskId)
	return JSONResponse(raw)

@app.get("/tasks/{taskId}/files/{fileName}", summary="Retrieve a binary result of a task")
async def getTaskResultFile(taskId: str, fileName: str):
	stream = await engine.getResultFile(taskId, fileName)
	return StreamingResponse(stream, media_type="application/octet-stream")

@app.post("/services", summary="Create a new service or pipeline")
async def createService(service: Union[interface.ServiceDescription, interface.PipelineDescription]):
	if service.type is interface.ServiceType.SERVICE:
		api = service.api.dict()
		serviceName = api["route"]
		if serviceName not in engine.endpoints:
			await engine.createServicePipeline(service.url, api)
			addRoute(**api)
	elif service.type is interface.ServiceType.PIPELINE:
		api = await engine.addPipeline(service.dict())
		addRoute(**api)

@app.get("/services", summary="Get all pipelines", response_model=List[interface.PipelineDescription])
async def getPipelines():
	pipelines = await engine.getPipelines()
	return pipelines

@app.get("/stats", summary="Get engine and pipelines statistics")
async def getTaskRaw():
	stats = await engine.getStats()
	return JSONResponse(stats)

@app.delete("/services/{serviceName}", summary="Remove a service or pipeline")
async def removeService(serviceName: str):
	if serviceName in engine.endpoints:
		await engine.removePipeline(serviceName)
		for i in range(len(app.routes)):
			if app.routes[i].path == "/services/" + serviceName:
				app.routes.pop(i)
				break
		# Force the regeneration of the schema
		app.openapi_schema = None

@app.get("/services/{serviceName}", summary="Get the pipeline description", response_model=interface.PipelineDescription)
async def getPipeline(serviceName: str):
	pipeline = await engine.getPipeline(serviceName)
	return pipeline

@app.post("/processing", include_in_schema=False)
async def processCallback(task_id: str, request: Request):
	error = False
	errorMsg = ""

	data = {}
	binaries = []
	
	contentType = request.headers["content-type"].replace(";", "")

	if "application/json" in contentType:
		requestData = await request.json()
		if "type" in requestData and requestData["type"] == "error":
			error = True
			errorMsg = requestData["message"] if "message" in requestData else ""
		else:
			data.update(requestData)
	elif "multipart/form-data" in contentType:
		form = await request.form()
		for k in form:
			obj = form[k]
			if obj.content_type == "application/json":
				payload = await obj.read()
				data.update(json.loads(payload))
			else:
				data[k] = obj
				binaries.append(k)
	
	if error:
		await engine.processError(task_id, errorMsg)
	else:
		await engine.processTask(task_id, data, binaries)
