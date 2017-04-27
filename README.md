# newrelic_lvm_plugin

Docker's documentation recommend to use direct-lvm for the devicemapper storage.
This plugin permit the monitoring of the lvm's volume in **Newrelic**

**WARNING**: As the lvm information are only accessible with root privileges, this plugin have to be launch as root

# Dependency
* _python 2.7_ or _python 3_
- library requests
+ library daemonize

# Howto install:
## With pip:
You can install the plugin with pip 
```shell
sudo pip install nr_lvm_plugin
```

## With APT:
Add our GemFury repository in the apt's source list
```
echo "deb [trusted=yes] https://repo.fury.io/webgeoservices/ /" > \
/etc/apt/sources.list.d/fury.list
```
Then install the package
```
sudo apt-get install python3-newrelic-lvm-plugin 
```
Run it with systemd
```
service newrelic-lvm-plugin start
```
## From Sources:
First install the requirements
```shell
pip install -r requirements.txt
```

Then you can use directly the file nrlvmd.py

# Howto use it:
The script is a daemon, to start it you just have to launch the following command as root
```shell
sudo nrlvmd.py start
```

## Options:
* option -f run the daemon in foreground
- option -log let you define the loglevel (_default is CRITICAL_)
+ option -config is the path to the config file

## Configuration:
The script need 2 config values
* license_key: which is your Newrelic's licence key
+ hostname: The server's name that will appear in Newrelic's interface

By default the script read these two values from the nrsysmond config file `/etc/newrelic/nrsysmond.cfg`
If you want to define your own config file, it have to look like this
```shell
license_key=your_licence_key
hostname=server_name
```

You can also define this two values with environments variables
```shell
export NEWRELIC_LICENCE_KEY=your_licence_key
export NEWRELIC_HOSTNAME=server_name
```

If hostname is not defined in the config file or in the environments variables, the script use the server's hostname
