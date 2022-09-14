# testtask_DataOX

#How to launch project
1) Clone project `git clone https://github.com/NazikM/testtask_DataOX.git`.
2) Create venv `python -m venv venv` and activate it [depend on system](https://www.infoworld.com/article/3239675/virtualenv-and-venv-python-virtual-environments-explained.html).
3) Run `pip install -r requirements.txt` to install all requirements.
4) Run `docker run --name test-postgres -p 5433:5432 -e POSTGRES_PASSWORD=password -d postgres:latest` to startup postgres in Docker container with external port `5433` and `password`.
5) Run main sreipt to parse the site `python main.py`.
