#!/bin/bash

python3 -m venv env
. env/bin/activate

pip install setuptools
pip install wheel

cp -r ../server ./imaginarium_server
cd imaginarium_server
mkdir -p ru/LC_MESSAGES
mkdir -p resources/cards
msgfmt -o ru/LC_MESSAGES/server.mo ru.po
cd ../
if [ -f ./db.zip ] ; then
	cp db.zip imaginarium_server/resources/cards ;
else
	echo "Error: no resource file for server found."
	rm -r imaginarium_server
	exit ;
fi

python3 setup_server.py bdist_wheel
rm -r build
rm -r imaginarium_server

cp -r ../imaginarium ./
cd imaginarium/interface
mkdir -p ru/LC_MESSAGES
msgfmt -o ru/LC_MESSAGES/client.mo ru.po
cd ../..

python3 setup_client.py bdist_wheel
rm -r build
rm -r imaginarium
