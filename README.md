# itxia-docker
##安装docker以及docker-compose
[install docker in ubuntu]
[install docker in ubuntu]: https://docs.docker.com/v1.7/docker/installation/ubuntulinux/
[install docker-compose in ubuntu]
[install docker-compose in ubuntu]: https://docs.docker.com/v1.7/compose/install/

##git仓库
`git clone https://github.com/imphoney/itxia-docker.git`

##启动docker
`cd itxia-docker`  
`sudo docker-compose up ` 

##mysql初始化
`cd itxia-docker`
```
sudo docker-compose run --rm website python manage.py db init
sudo docker-compose run --rm website python manage.py db migrate -m 'new' \
sudo docker-compose run --rm website python manage.py db upgrade \
sudo docker-compose run --rm website python manage.py testdb 

###最好做这一步
`sudo docker-compose stop` 
`sudo docker-compose up` 

##测试api
`cd itxia-docker`  

`pip install -r requirements.txt`  

`python client_test.py`  
`

