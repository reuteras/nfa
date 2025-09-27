#!/usr/bin/env python3
"""nfa - nfstream for Arkime."""
import configparser
import json
import re
import sys
import typing
import urllib.parse as ul
from pathlib import Path

import dateutil.parser as dp
import requests
from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from nfstream import NFStreamer
from pydantic_settings import BaseSettings
from requests.auth import HTTPDigestAuth
from starlette.responses import Response
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

config = configparser.ConfigParser()
config.read('config.ini')
session = requests.Session()
session.verify = False
disable_warnings(category=InsecureRequestWarning)


# pylint: disable=R0903
class PrettyJSONResponse(Response):
    """Class to pretty print json response."""
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        """Render function for PrettyJSONResponse."""
        return json.dumps(
                content,
                ensure_ascii=False,
                allow_nan=False,
                indent=4,
                separators=(", ", ":"),
                ).encode("utf-8")

# pylint: disable=R0903
class Settings(BaseSettings):
    """Settings class."""
    api_username: str = "username"
    api_password: str = "password"
    api_url: str = "http://server.example.com:8009"
    api_domain: str = "example.com"
    api_port: str = "8005"
    api_proto: str = "http://"
    api_tempdir: str = "tmp"
    api_multi: bool = True

    if config['api']['username'] != "":
        api_username = config['api']['username']
    if config['api']['password'] != "":
        api_password = config['api']['password']
    if config['api']['url'] != "":
        api_url = config['api']['url']
    # Allow domain to be empty
    api_domain = config['api']['domain']
    try:
        api_multi = config['api']['multi']
    except KeyError:
        api_multi = True

    if config['api']['port'] != "":
        api_port = config['api']['port']
    if config['api']['proto'] != "":
        api_proto = config['api']['proto']
    if config['api']['tempdir'] != "":
        api_tempdir = config['api']['tempdir']

settings = Settings()
app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

def date_to_timestamp(parsetime):
    """Return unix timestamp from ISO 8601 date."""
    parsed_time = dp.parse(parsetime)
    timestamp = int(parsed_time.timestamp())
    return str(timestamp)

def clean_root_id(input_id):
    """If root_id includes a : remove it and everything before it."""
    if re.search(r":", input_id):
        return input_id.split(':')[1]
    if re.search(r"@", input_id):
        return input_id.split('@')[1]
    return input_id

def query_arkime(start, stop, query, field):
    """Query Arkime API."""
    base_url = settings.api_url + '/unique.txt?graphType=lpHisto&seriesType=bars&length=50'

    query_url = base_url + \
            "&startTime=" + start + \
            "&stopTime=" + stop + \
            "&expression=" + ul.quote_plus(query) + \
            "&exp=" + field

    if settings.api_multi:
        result = requests.get(query_url, verify=False, timeout=60, \
                auth=HTTPDigestAuth(settings.api_username, settings.api_password))
    else:
        result = requests.get(query_url, verify=False, timeout=60)
    if result.status_code != 200: # noqa PLR2004
        print(result.content.decode())
        raise HTTPException(status_code=404, detail="Item not found")
    return result.content.decode()

def get_rootid_from_sessionid(start, stop, session_id):
    """If there is a rootid for the id return that."""
    root_id = query_arkime(start, stop, "id == " + session_id, "rootId")

    if root_id == "":
        root_id = session_id

    return root_id.strip()

def retrive_pcap_from_sessionid(start, stop, node, rootid, limit=2000):
    """Retrieve pcap for id and and save as <id>.pcap in tempdir."""
    if settings.api_multi:
        pcap_file = Path(settings.api_tempdir + '/' + node + '-' + rootid + '.pcap')
    else:
        pcap_file = Path(settings.api_tempdir + '/' + rootid + '.pcap')

    if not pcap_file.is_file():
        query = 'id == ' + rootid
        if settings.api_multi:
            base_url = settings.api_proto + node + settings.api_domain + ':' + \
                    settings.api_port + '/sessions.pcap?length=' + str(limit)
        else:
            base_url = settings.api_url + ':' + \
                    settings.api_port + '/sessions.pcap?length=' + str(limit)
        url = base_url + \
                "&startTime=" + start + \
                "&stopTime=" + stop + \
                "&expression=" + ul.quote_plus(query)

        try:
            if settings.api_multi:
                pcap_data = requests.get(url, verify=False, timeout=300, \
                        auth=HTTPDigestAuth(settings.api_username, settings.api_password))
            else:
                pcap_data = requests.get(url, verify=False, timeout=300)
        except (requests.ConnectionError, requests.HTTPError, requests.Timeout) as error:
            print(error)
            sys.exit()

        pcap_file.write_bytes(pcap_data.content)
    return pcap_file

def get_nfstream_info(input_id, iso_start, iso_stop, node):
    """Returns the nfstream result for the first flow (and only flow) in the pcap."""
    nfstream_result = {}

    start = date_to_timestamp(iso_start)
    stop =  date_to_timestamp(iso_stop)
    session_id = clean_root_id(input_id)
    root_id = get_rootid_from_sessionid(start, stop, session_id)
    pcap_file = retrive_pcap_from_sessionid(start, stop, node, root_id, 30)

    try:
        stream = NFStreamer(str(pcap_file),
            decode_tunnels=True,
            bpf_filter=None,
            promiscuous_mode=True,
            snapshot_length=1536,
            idle_timeout=120,
            active_timeout=1800,
            accounting_mode=0,
            udps=None,
            n_dissections=20,
            statistical_analysis=False,
            splt_analysis=0,
            n_meters=0,
            performance_report=0
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail="NFStreamer failed: " + exc) from exc

    for flow in stream:
        for key in flow.keys():
            nfstream_result[key] = getattr(flow, key)
        # Should only be one flow so break
        break

    pcap_file.unlink()
    return nfstream_result

# Handle urls.

@app.get("/")
async def root():
    """Print default message."""
    return PrettyJSONResponse({ \
            "message": "Get nfstream result for one rootid from Arkime.", \
            "Basic json": "/rootid/<rootid>", \
            "Prettyprint json": "/visual_json/<rootid>", \
            "FastAPI": "/docs"})

@app.get("/rootid/{input_id}")
async def get_rootid(input_id: str, iso_start: str = "1970-01-01T00:00:00.000Z", \
        iso_stop: str = "2100-12-31T23:59:59.000Z", node: str = "node"):
    """Get parameters from Arkime and return nfstream results as raw json."""
    data = get_nfstream_info(input_id, iso_start, iso_stop, node)

    return json.loads(json.dumps(data))

@app.get("/visual_rootid/{input_id}")
async def get_visual_rootid(input_id: str, iso_start: str = "1970-01-01T00:00:00.000Z", \
        iso_stop: str = "2100-12-31T23:59:59.000Z", node: str = "default-arkime-node"):
    """Get parameters from Arkime and return pretty printed nfstream results."""
    data = get_nfstream_info(input_id, iso_start, iso_stop, node)

    return PrettyJSONResponse(data)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Helper function for swagger."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    """Helper function for swagger."""
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Helper function for redoc."""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )
