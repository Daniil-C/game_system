Start
=====

Client and server are started as modules using python -m module_name

Environment variables
---------------------

Client:
        LC_ALL - localization.

Server:
*        LC_ALL - localization,
*        HOST_IP - ip address (default: localhost),
*        PORT - server port (default: 7840),
*        LOG_FILE - path  to file, used for logging (default: package_path/server.log),
*        RESOURCES_VERSION - set version of resource pack. This value is overriden by value in version.json.


Client start command
--------------------

python -m imaginarium

Server start command
--------------------

python -m imaginarium_server
