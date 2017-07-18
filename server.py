import hashlib
import hmac
import json

import requests
from flask import Flask
from flask import request

import config
from payload import PullRequest, PullRequestComment, Issue, IssueComment, Repository, Branch, Push, Tag, CommitComment, \
    Wiki

app = Flask(__name__)

SECRET = hmac.new(config.SECRET, digestmod=hashlib.sha1) if config.SECRET else None


@app.route((config.SERVER['hook'] or '/') + '<hook_id>/<channel>', methods=['POST'])
def root(hook_id, channel):
    if request.json is None:
        print 'Invalid Content-Type'
        return 'Content-Type must be application/json and the request body must contain valid JSON', 400

    if SECRET:
        signature = request.headers.get('X-Hub-Signature', None)
        sig2 = SECRET.copy()
        sig2.update(request.data)

        if signature is None or sig2.hexdigest() != signature.split('=')[1]:
            return 'Invalid or missing X-Hub-Signature', 400

    data = request.json
    event = request.headers['X-Github-Event']

    msg = ""
    if event == "ping":
        msg = "ping from %s" % data['repository']['full_name']
    elif event == "pull_request":
        if data['action'] == "opened":
            msg = PullRequest(data).opened()
        elif data['action'] == "closed":
            msg = PullRequest(data).closed()
        elif data['action'] == "assigned":
            msg = PullRequest(data).assigned()
    elif event == "issues":
        if data['action'] == "opened":
            msg = Issue(data).opened()
        elif data['action'] == "closed":
            msg = Issue(data).closed()
        elif data['action'] == "labeled":
            msg = Issue(data).labeled()
        elif data['action'] == "assigned":
            msg = Issue(data).assigned()
    elif event == "issue_comment":
        if data['action'] == "created":
            msg = IssueComment(data).created()
    elif event == "repository":
        if data['action'] == "created":
            msg = Repository(data).created()
    elif event == "create":
        if data['ref_type'] == "branch":
            msg = Branch(data).created()
        elif data['ref_type'] == "tag":
            msg = Tag(data).created()
    elif event == "delete":
        if data['ref_type'] == "branch":
            msg = Branch(data).deleted()
    elif event == "pull_request_review_comment":
        if data['action'] == "created":
            msg = PullRequestComment(data).created()
    elif event == "push":
        if not (data['deleted'] and data['forced']):
            if not data['ref'].startswith("refs/tags/"):
                msg = Push(data).commits()
    elif event == "commit_comment":
        if data['action'] == "created":
            msg = CommitComment(data).created()
    elif event == "gollum":
        msg = Wiki(data).updated()

    if msg:
        post(msg, config.WEBHOOK_URL.rstrip('/') + '/' + hook_id, channel)
        return "Notification posted to Mattermost"
    else:
        return "Not implemented", 400


def post(text, url, channel):
    data = {}
    data['text'] = text
    data['channel'] = channel
    data['username'] = config.USERNAME
    data['icon_url'] = config.ICON_URL

    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

    if r.status_code is not requests.codes.ok:
        print 'Encountered error posting to Mattermost URL %s, status=%d, response_body=%s' % (
        url, r.status_code, r.json())

if __name__ == "__main__":
    app.run(
        host=config.SERVER['address'] or "0.0.0.0"
        , port=config.SERVER['port'] or 5000
    )
