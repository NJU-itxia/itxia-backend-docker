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
`sudo docker-compose up --no-build` 

##mysql初始化
`cd itxia-docker`
```
sudo docker-compose run --rm website python manage.py db init \
&& python manage.py db migrate -m 'new' \
&& python manage.py db upgrade \
&& python manage.py testdb  

##测试api
`cd itxia-docker`  

`pip install -r requirements.txt`  

`python client_test.py`  
`

