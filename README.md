Virtual-2-Container
===================

This simple script will take a virtual disk and convert it into a
docker container.  It has two modes of operating.  It can create a
full image based purely on the content of the virtual disk, or it can
create a layer on top of an existing image, trying to avoid duplication.
It uses rsync and file checksumming to detect files that are identical
between the base image and the virtual disk content.

If you've got a single, simple app, you can then run it directly with
docker from the commandline.   If the app contains multiple services,
then you can use Compose and/or multiple Dockerfiles to define them for
quick instantiation.


Dependencies
------------

In order to use this tool, you'll have to install docker, as well
as [libguestfs-tools](http://libguestfs.org/)

