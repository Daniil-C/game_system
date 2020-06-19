Installation
============

Project is packed into two wheel packages.
Package 'imaginarium' contains game client, 'imaginarium_server' contains
game server.

Requirements
------------

Client:
        * Python version 3.6 or higher.
        * Dependencies:
          pygame,
          wget.
Server:
        * Python version 3.7 or higher.

Package building
----------------

1. Download archive with cards using link in README.md. Put it into
   'distribution' directory.
2. Run the following commands:
        1. cd distribution
        2. make build
3. A 'dist' directory, containing wheel packages, will appear.
4. Run 'make clean' command to remove build files.
5. Install packages using module 'pip'.
