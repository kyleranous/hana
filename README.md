# HANA
Home Automation Networked Assistant

HANA is a Home Automation Server management tool with the goal of making the setup and management of Docker Swarms easier. It is built with Django 4.0.3 and uses [Docker API v1.41](https://docs.docker.com/engine/api/v1.41/). Hana contains both a UI and an API to assist with integration with other Automation programs like Home Assistant and Node-Red. HANA is intended to be used with nodes running linux.

I am using this project to test and learn multiple frameworks/strategies. While I try to maintain consistent look and structure through the project, there is some variation. 

**NOTE**:<br>
HANA requires the nodes in the swarms to expose their ports and depending on configuration will run commands as a root user. Currently there is no support for TLS or certificates (On Development Roadmap). If you are using Hana, ***DO NOT*** expose it outside of your network.

**Frameworks Used:**
 - Django 4.0.3
 - Django Rest 3.13.1
 - Bootstrap 5
 - drf-yasg 1.20
 
Current Version: 0.1a

---
### Features
**V0.1a**
 - **UI**
   - Add existing swarms to be tracked by the system
   - Swrm Dashboard that displays basic status information on the Swarm and nodes.
   - Node detail pages that display CPU and memory Usage an list services being run on the node.

- **API**
  - Endpoints to View Tracked / Add Existing Swarms, and Retrieve a list of nodes belonging to a swarm


### Planned Features

 - [ ] Get real-time status on existing Swarms
 - [ ] Guided Swarm Setup - Setup a Swarm from scratch through the Hana UI
 - [ ] Single Click Image Deployment - Quickly Deploy common images on swarms
 - [ ] Service Dashboard - Dashboard with links to active services that have a web UI
 - [ ] Swarm Health Checks / Recommendations
 - [ ] Implement TLS on Docker API and Manage Certificates through HANA
 - [ ] Create and manage distributed storage volumes using GlusterFS or Ceph
 - [ ] Browser-based terminal emullator and ssh client for accessing nodes using xterm.js
 - [ ] Private Container Registry creation and management

---

## Installation

1. Clone repository `git clone https://github.com/silverback338/hana.git`
1. Create a virtual environment `python3 -m venv venv`
1. Activate virtual environment `source venv/bin/activate` on linux or `venv\scripts\activate` on Windows
1. Install dependencies from requirements.txt `pip install -r requirements.txt`
1. Initiate SQLite Database for testing/evaluation `python3 hana/manage.py migrate`
1. Run Unit Tests to make sure everything is configured correctly `python3 hana/manage.py test`
1. Create SuperUser `python3 hana/manage.py createsuperuser`
1. Run the Server `python3 hana/manage.py runserver` to be accessable to local machine only `python3 hana/manage.py runserver 0.0.0.0:8000` to be accessable on local network. Default port is 8000


### Configuring Docker Engine to recieve HTTP requests
Each Docker node needs to be configured to accept HTTP requests to work with HANA. 

Connect to each node and make the following changes:
1. Open docker.service `nano /lib/systemd/system/docker.service`. Depending on your stup, you may require root permissions.
1. Find the line that starts with `ExecStart` and add `-H=tcp://0.0.0.0:2375` to the end of the line. This will open up the node to be accessed via an HTTP request. Note Port 2375 is the default port Hana will assign to each node. If you want to use a different port, the ports can be updated on each node from the admin panel.
1. Save the file
1. Reload the docker daemon `systemctl daemon-reload`
1. Restart the Docker service `service docker restart`


### Viewing the API Documentation
Once launched, API documentation can be viewed at `[BASE_ADDRESS]/docs/api`