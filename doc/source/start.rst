Start
=====

Client and server are started as modules using python -m module_name

Environment variables
---------------------

Client:

* LC_ALL - localization,
* CONFIG - overrides path to configuration file (default:
  package_path/backend/config.json).

Server:

* LC_ALL - localization,
* HOST_IP - ip address (default: localhost),
* PORT - server port (default: 7840),
* LOG_FILE - path  to file, used for logging (default: package_path/server.log),
* RESOURCES_VERSION - set resource pack version. This value is overriden by
  value in version.json,
* RESOURCEPACK - set link for resource pack downloading. If not set,
  server will use link to its resource server.


Client start command
--------------------

python -m imaginarium

Server start command
--------------------

python -m server
