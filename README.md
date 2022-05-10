# MyGeneset.info

MyGeneset.info is a web API for accessing gene set data.

## Setting Up and Running BioThings Hub

#### 1. Pre-requisites:

- Python>=3.6  (Python versions lower than 3.8 also require PyPI package `singledispatchmethod`)
- Git
- MongoDB
- Elasticsearch>=6.0.0

Elasticsearch and MongoDB can be installed locally, or run from Docker containers:

MongoDB:

    docker run -d -p 27017-27019:27017-27019 --name mongodb mongo:latest

Elasticsearch:

    docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:7.17.1

#### 2. Clone this repo:


    git clone https://github.com/biothings/mygeneset.info.git


#### 3. Setup a Python virtual environment (optional, but highly recommended):

With virtualenv:

    mkdir -p ~/venvs
    virtualenv ~/venvs/mygeneset
    source ~/venvs/mygeneset/bin/activate

Alternatively, using miniconda:

    conda create -n mygeneset python=3.8
    conda activate mygeneset

#### 4. Install required Python modules:


    cd mygeneset.info
    pip install -r ./requirements_hub.txt

#### 5. Make your own "config.py" file


    cd src
    vim config.py

   >from config_hub import *
   >\# Add additional customizations

#### 6. Generate SSH keys

    # from src folder:
    ssh-keygen -f bin/ssh_host_key

#### 7. Start BioThings Hub

    # from src folder:
    python -m bin.hub

#### 8. Connect to the Hub from web interface (BioThings Studio)

Navigate to https://studio.biothings.io/ and create a connection to `http://localhost:HUB_API_PORT`,
in which `HUB_API_PORT` is the port number specified in your configuration (default is 19480).

## Setting up the Web Server

#### 1. Pre-requisites:

MongoDB is not required for running the web server

- Python>=3.6  (Python versions lower than 3.8 also require PyPI package `singledispatchmethod`)
- Git
- Elasticsearch>=6.0.0 (See installation steps above)


### 2. Install requirements

    pip install -r ./requirements_web.txt


### 3. Configure the Web Component

The API configuration file is located under `/src/config_web.py`.

The value of STATUS_CHECK.id should match an `_id` in the data.

    STATUS_CHECK = {
        'id': 'WP4966',
        'index': 'mygeneset_current',
        'doc_type': 'geneset'
    }

You can override any settings from `config_web.py` in `config.py`:

   >from config_web import *
   >\# Add additional customizations


Some required configurations:

```python
# A random string
COOKIE_SECRET =

# GitHub keys
GITHUB_CLIENT_ID =
GITHUB_CLIENT_SECRET =

# ORCID keys
ORCID_CLIENT_ID =
ORCID_CLIENT_SECRET =

WEB_HOST = "http://localhost:8000"

# Path to local webapp folder
FRONTEND_PATH =
```

`FRONTEND_PATH` is only required for running the API with the user interface. You need to first clone and build the web app project: https://github.com/biothings/mygeneset.info-website

### 4. Create Elasticsearch Indices

The ES indices defined in the `ES_INDEX` setting must exist.

For example:

```bash
# Creating an empty user_genesets index
curl -X PUT "localhost:9200/user_genesets"
```
### 5. Run API

`python index.py`

For launching alongside the web app:

`python index.py --webapp`
