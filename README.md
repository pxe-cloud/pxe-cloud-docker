# PXE Cloud Docker
This is the repository that contains all the files and sources for the Docker containers and composers. If you want to get more info about the project, check the [main repository](https://github.com/pxe-cloud/pxe-cloud).

There are two servers in this repository:



## Local Server:

This is the server that the majority of users are going to use. It's simply a DHCP server that loads an iPXE binary that is pointing to the main login menu. To install it, you need to execute the following commands in the server machine:

```bash
git clone https://github.com/pxe-cloud/pxe-cloud-docker
cd pxe-cloud-docker/
# Make sure all the settings are correct
nano settings.yml
cd local/
# Note: in case you don't have a Debian or an Ubuntu (or derivates), just check the packages installed and install them manually. Finally execute `./start.py`
./install_ubuntu_debian.sh
```

 

You just need to answer the questions that are going to be asked. In case you already have a DHCP server, answer `No` when being asked about the DHCP configuration and add the following lines in your DHCP configuration:

```
# PXE Config
allow booting;
allow bootp;
next-server <SERVER IP>;
filename "undionly.kpxe";
```

Where `<SERVER IP>` is the IP address of the machine where all the previous code was executed in



## Questions?

In case you need help or you have a question, just open an issue and we'll be happy to help you! 

## Demo installation  
  
[![Demo installation](https://preview.ibb.co/cOsRjd/Captura_de_pantalla_de_2018_06_13_19_30_25.png)](https://www.youtube.com/embed/6BVTzLfp320)  
  
  
