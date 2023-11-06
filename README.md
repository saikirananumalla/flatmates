# roommates

#install condo for managing python packages

#create virtual env
`conda create -n dbms python=3.7.1`

#activate
`conda activate dbms`

#install fastapi
`conda install -c conda-forge fastapi`

#install sqlalchemy
`conda install -c anaconda sqlalchemy`

install pymysql
`conda install -c anaconda pymysql`

install uvicorn
`conda install -c conda-forge uvicorn-standard`

#run app
`uvicorn app:app --reload`
