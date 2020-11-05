# MyGeneset.info

MyGeneset.info is a web API for accessing gene set data.

## Setting Up and Running BioThings Hub

#### 1. Pre-requisites:

- Python>=3.6  (Python versions lower than 3.8 also require PyPI package `singledispatchmethod`)
- Git
- MongoDB
- Elasticsearch>=6.0.0, <7.0.0

Elasticsearch and MongoDB can be installed locally, or run from Docker containers:

MongoDB:

    docker run -d -p 27017-27019:27017-27019 --name mongodb mongo:latest

Elasticsearch:

    docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:6.8.13

#### 2. Clone this repo:


    git clone https://github.com/biothings/mygeneset.info.git


#### 3. Setup a Python virtual environment (optional, but highly recommended):

With virtualenv:

    mkdir ~/venvs
    virtualenv ~/venvs/mygeneset
    source ~/venvs/mygeneset/bin/activate


Alternatively, using miniconda:

    conda create -n mygeneset python=3.8
    conda activate mygeneset


#### 4. Install required Python modules:


    pip install -r ./requirements_hub.txt


#### 5. Make your own "config.py" file


    cd src
    vim config.py
    
   >from config_web import *  
   >\# Add additional customizations

#### 6. Generate SSH keys

    # from src folder:
    ssh-keygen -f bin/ssh_host_key

#### 7. Start BioThings Hub

    # from src folder:
    python -m bin.hub

#### 8. Connect to the Hub from web interface (BioThings Studio)

Navigate to https://studio.biothings.io/ and create a connection to http://localhost:HUB_API_PORT