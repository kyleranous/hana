#!/bin/sh

sudo cp -rf app.conf /etc/nginx/conf.daemon
sudo cp app.conf /etc/nginx/sites-enabled

sudo usermod -aG jenkins nginx
chmod 710 /var/lib/jenkins/workspace/HANA-TEST

sudo nginx -then

sudo systemctl reload nginx

sudo systemctl restart nginx

sudo systemctl status nginx