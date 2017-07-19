# Github integration for Mattermost

Fork of https://gitlab.dynamictivity.com/dynamictivity/mattermost-integration-github

Inspired by [mattermost-integration-gitlab](https://github.com/NotSqrt/mattermost-integration-gitlab) this program creates a server using [flask](https://github.com/mitsuhiko/flask) that listens for incoming GitHub event webhooks. These are then processed, formatted, and eventually forwarded to Mattermost where they are displayed inside a specified channel.
![](preview.png)

## Requirements
- Python
- Flask (install with `pip install flask`)
- requests (install with `pip install requests`)
- (optional) PIL (install with `pip install pillow`) - needed to hide big Github avatars

## Usage
Copy `config.template` to `config.py` and edit it with your details. For example:

```python
USERNAME = "Github"
ICON_URL = "https://yourdomain.org/github.png"
MATTERMOST_WEBHOOK_URL = "https://yourdomain.org/hooks/"
SECRET = 'secretkey'
SHOW_AVATARS = True
SERVER = {
    'hook': "/"
,   'address': "0.0.0.0"
,   'port': 5000
}
```

The server is listening by default on address `0.0.0.0`, port `5000`, and
using `/` as base route.
Point your Github webhooks to `http://yourdomain.org:5000/hook_id/channel`.
Github notifications will then be delegated to the hook identified via `hook_id` and
posted in the channel `channel`.

Channel names need to use the spelling that is used in their URL (the channel ID), e.g. instead
of `Town Square` it needs to be `town-square`.

If you have a proxy/load-balancer in front of your machine, and do not want to
expose port 5000 to the outside, change the `SERVER['hook']` value and redirect it
to this service.
For example, if `SERVER['hook']` is `/hooks/github`, your Github webhooks
would be `http://yourdomain.org/hooks/github/hook_id/channel`.

If you don't want to use a secret set the field to `None`.

Start the server with `python server.py`.

## Docker

This image is available on [DockerHub](https://hub.docker.com/r/dynamictivity/mattermost-integration-github/)

To run this, use the following `docker-compose.yml` while adjusting the settings for your own requirements:

```yaml
version: '2'
services:
  mm-int:
    image: dynamictivity/mattermost-integration-github
    environment:
      FLASK_DEBUG: 1
      MATTERMOST_WEBHOOK_URL: "https://mattermost.dynamictivity.com/hooks/"
    ports:
      - "5000:5000"
```

### Deploying with Docker

To deploy with Docker, make sure you have Docker installed and run:

```
docker build -t mm-int-github .
docker run mm-int-github -p 5000:5000 -d
```


## Supported Events

Not all Github events are forwarded to Mattermost. Currently supported events are:

* Ping events (send when first adding the Github webhook)
* Commit pushes and comments
* Issues (open, close, comment)
* Pull Requests (create, merge, remove, comment)
* Create/Delete repositories
* Create/Delete branches and tags

All other events will report back to GitHub with `400 Not Implemented`.

## Known issues

- If you set a custom username (as shown in the default config), make sure you also set **Enable webhooks and slash commands to override usernames** under **Custom Integrations** in the System Console to **True**. Otherwise the bots username will be that of the person that setup the Mattermost integration.
