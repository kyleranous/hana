# HANA Style Guide

This document provides guidence on project structure and conventions used throughout. If contributing to this project, please reference this document and make sure your contribution follows these guidelines. 


## Project Structure
HANA has both a UI and API that is being developed in parallel. To keep things simple, all UI functions will be in the parent folder of the app as django boilerplate sets up. Each app will also container an API directory that will contain the API. The parent api folder will contain a `urls.py` file and directoryies for the API Versions(See API versioning section). Each API version directory will have all the files needed for the API.

```
HANA
│   manage.py    
│
└───swarman # Parent app directory holds UI functions and features
│   │   context_processors.py
│   │   models.py
|   |   urls.py
|   |   views.py
│   │
│   └───api # api directory in the app holds API functins and features
│       │   urls.py
|       └───v1_0
            |   api_utils.py
│           │   api_views.py
│           │   serializers.py
|           |   urls.py
│   
└───docs # Holds reference information for users and contributors
    │   styleguide.md

```

## API

### Versioning
API Versioning will be a simple [MAJOR].[minor] numbering system. The first version will always be 1.0. If an API update changes the endpoints or output of existing endpoints that would potentially break any implementation that is currently using the API, the Major version will be incremented and the minor version reset to 0. Added functionality, optimizations, or corrections that doesnt change existing endpoints or change what is returned by the endpoints will have a new minor version.

If someone creates a script using API version 1.2, then API 1.4 should still work for them without them having to refactor their code. However a script using API 1.2 may not function with API 2.1.

### Naming Conventions

 - URL names: kabab-case with each name prepended with api- ex `api-swarm-detail`
 - 

 ## UI

 ### Colors

 **Status Colors**
 | Status | Color (Hex) |
 | :---: | :--- |
 | Running | |
 | Paused | |
 | Degraded | #F36411 |
 | Error | |
 | Drain | |