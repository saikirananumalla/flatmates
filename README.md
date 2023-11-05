# roommates

#install condo for managing python packages

#create virtual env
`conda create -n dbms`

#activate
`conda activate dbms`

#install fastapi
`conda install -c conda-forge fastapi`

#install sqlalchemy
`conda install -c anaconda sqlalchemy`

#install mysqlclient
`conda install -c conda-forge mysqlclient`

#run app
`uvicorn app:app --reload`
