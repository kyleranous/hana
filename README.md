# HANA
Home Automation Networked Assistant

HANA is a Home Automation Server management tool with the goal of making the setup and management of Docker Swarms easier. It is built with Django 4.0.3 and uses [Docker API v1.41](https://docs.docker.com/engine/api/v1.41/). Hana contains both a UI and an API to assist with integration with other Automation programs like Home Assistant and Node-Red.

I am using this project to test and learn multiple frameworks/strategies. While I try to maintain consistent look and structure through the project, there is some variation. 

**NOTE**:<br>
**HANA requires the nodes in the swarms to expose their ports and depending on configuration will run commands as a root user. Currently there is no support for TLS or certificates (On Development Roadmap). If you plan on using Hana, *DO NOT* expose it outside of your network.** 

Current Version: 0.1a

### Features
**V0.1a**
 - **UI**
   - Add existing swarms to be tracked by the system
   - Swrm Dashboard that displays basic status information on the Swarm and nodes.
   - Node detail pages that display CPU and memory Usage an list services being run on the node.

- **API**
  - Endpoints to View Tracked / Add Existing Swarms, and Retrieve a list of nodes belonging to a swarm


### Planned Features
 - Guided Swarm Setup - Setup a Swrm from scratch through the Hana UI
 - Single Click Image Deployment - Quickly Deploy Common images on swarms
 - Service Dashboard - Gridded Dashboard with links to active services with a Web UI
 - Swarm Health Checks / Recommendations

---

## Installation
1. Clone repository `git clone https://github.com/silverback338/hana.git`
1. Create a virtual Environment `python3 -m venv venv`
1. Activate Virtual Environment `source venv/bin/activate` on linux or `venv\scripts\activate` on Windows
1. Install Dependencies from requirements.txt `pip install -r requirements.txt`
1. Initiate SQLite Database for testing/evaluation `python3 hana/manage.py migrate`
1. Run Unit Tests to make sure everything is configured correctly `python3 hana/manage.py test`
1. Create SuperUser `python3 hana/manage.py createsuperuser`
1. Run the Server `python3 hana/manage.py runserver` to be accessable to localhost machine only `python3 hana/manage.py runserver 0.0.0.0:8000` to be accessable on local network. Default port is 8000

