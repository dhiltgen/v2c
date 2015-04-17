#!/usr/bin/env python

import argparse
import subprocess


def get_rsync_install_cmd(image_name):
    cmd = ['docker', 'run', '--rm', image_name, 'bash', '-c',
           'if $(which rsync>/dev/null) ; then echo "rsync";'
           'elif $(which yum>/dev/null); then echo "yum -y install rsync";'
           'elif $(which apt-get>/dev/null); then echo "apt-get update&&apt-get install -y rsync";'
           'else echo "unsupported";'
           'fi']
    res = subprocess.check_output(cmd)
    if res == 'rsync':
        return None
    elif res == 'unsupported':
        raise Exception("Unsupported image - we only support yum and apt-get based images")
    return res

def extract_tar(disk):
    try:
        return subprocess.Popen(['virt-tar-out', '-a', disk, '/', '-'],
                                stdout=subprocess.PIPE)
    except OSError:
        raise Exception("You must install the libguestfs-tools package first")


def smart_delta(tar_pipe, image, tag, rsync_install):
    if rsync_install:
        cmd = rsync_install.strip() + ' && '
    else:
        cmd = ''
    cmd += 'mkdir /overlay && cd /overlay && echo "processing tar"; ' + \
           'tar xf - && ' + \
           'rsync -crHpogtlW --stats --exclude=dev/ --exclude=etc/hostname ' + \
           '--exclude=etc/hosts --exclude=sys/ --exclude=etc/resolv.conf /overlay/ / ;' + \
           'rm -rf /overlay'
    print subprocess.check_output(['docker', 'run', '-i', '-a', 'stdin', '-a', 'stdout', '-a', 'stderr',
                                   '--name=' + tag, image, 'bash', '-c', cmd], stdin=tar_pipe.stdout)
    print subprocess.check_output(['docker', 'commit', tag, tag])
    print subprocess.check_output(['docker', 'rm', tag])


def main():
    """
    This simple tool will help convert a virtual disk image to a container image
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--disk", required=True,
                        help="The path to the virtual disk to import")
    parser.add_argument("--tag", required=True,
                        help="What to tag the final resulting image as")
    parser.add_argument("--base-image",
                        help="An optional docker base image to overlay this on")

    args = parser.parse_args()

    p = extract_tar(args.disk)
    if args.base_image:
        rsync_install = get_rsync_install_cmd(args.base_image)
        smart_delta(p, args.base_image, args.tag, rsync_install)
    else:
        res = subprocess.check_output(["docker", "import", "-", args.tag],
                                      stdin=p.stdout)
        print res


if __name__ == "__main__":
    main()
