sudo mkdir -p /srv/realms/etc /srv/realms/wiki 
sudo chmod 777 /srv/realms/wiki

sudo cp realms-wiki.json /srv/realms/etc

sudo docker run --name realms-wiki -p 5000:5000 -d --link postgresql:db \
 -v /srv/realms/wiki:/opt/wiki -v /srv/realms/etc:/etc/realms-wiki/ \
 realms-wiki-git

#sudo docker exec -it realms-wiki cp -r /home/deploy/realms-wiki/.venv/lib/python2.7/site-packages/realms/static /tmp/static

echo "sudo docker exec -it realms-wiki /usr/bin/tail -f /var/log/realms-wiki/realms-wiki.log"
