#!/usr/bin/env python3

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Script copyright (C) 2016, Bastien Montagne

"""
Usage
=====

Ubat Slicer has been developed to generate audio data conform to what's expected by French
Vigie-Chiro bats survey project [1], mostly because no good solution existed for GNU/Linux.

It will split wav files by channels and n seconds chunks (5 seconds by default, as expected by Vigie-Chiro).

Optionally, it can also perform some simple renaming to generate fully compatible filenames (avoids the extra
rename step prior to splitting audio files).

Note: provided you install FFMPEG and define ffmpeg/ffprobe executable paths, the script shall work on Windows as well…

[1] http://vigienature.mnhn.fr/page/vigie-chiro

Example
=======

Take raw wav files from ./raw_wav dir, rename them for circuit 601, year 2015, pass 1, and output their split versions
in current directory:

   wav_splitter.py -s ./raw_wav -d . -R -c 601 -y 2015 -p 1
"""

import os
import subprocess
import math


def argparse_create():
    import argparse
    global __doc__

    # When --help or no args are given, print this help
    usage_text = __doc__

    epilog = ""

    parser = argparse.ArgumentParser(description=usage_text, epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-s", "--source", dest="source_dir", metavar='PATH', required=True,
            help="Path to vigiechiro wav files")
    parser.add_argument("-d", "--dest", dest="dest_dir", metavar='PATH', required=True,
            help="Path to [--chunk-size]sec split files")

    parser.add_argument("-D", "--dryrun", dest="do_fake", default=False, action="store_true",
            help=("Do not actually do anything, only simulates (especially useful with renaming option)"))

    parser.add_argument(
        "--executable_ffmpeg", dest="executable_ffmpeg", default="ffmpeg", metavar='FFMPEG_EXECUTABLE',
        help="Path to the ffmpeg executable (on *nix you can usually leave it to default)")
    parser.add_argument(
        "--executable_ffprobe", dest="executable_ffprobe", default="ffprobe", metavar='FFPROBE_EXECUTABLE',
        help="Path to the ffprobe executable (on *nix you can usually leave it to default)")

    parser.add_argument("--chunk-size", dest="chunk_size", default=5, type=int,
            help="Size (length) of audio chunks to generate (in seconds, 5 by default)")

    parser.add_argument("-R", "--rename", dest="do_rename", default=False, action="store_true",
            help=("Take all wav files in given dir and rename them to proper format "
                  "(using sorted raw file names to order)"))
    parser.add_argument("-c", "--circuit", default="000", help="The identifier of your circuit")
    parser.add_argument("-y", "--year", default=0, type=int, help="The year")
    parser.add_argument("-p", "--pass", dest="npass", default=0, type=int, help="The pass number")

    return parser


def main():
    # ----------
    # Parse Args

    args = argparse_create().parse_args()
    files=[]

    if args.do_fake:
        print("WARNING! Dry run mode, no change will be applied...")

    if args.do_rename:
        for n, f in enumerate(sorted((f for f in os.listdir(args.source_dir) if f.endswith(".wav")))):
            new_name = "Cir%s-%d-Pass%d-Tron%d-Chiro.wav" % (args.circuit, args.year, args.npass, n + 1)
            fi = os.path.join(args.source_dir, f)
            fo = os.path.join(args.source_dir, new_name)
            if args.do_fake:
                files.append(f)
                print("Would rename '%s' to '%s'" % (fi, fo))
            else:
                files.append(new_name)
                print("Renaming '%s' to '%s'" % (fi, fo))
                os.rename(fi, fo)
    else:
        files = [f for f in os.listdir(args.source_dir) if "-Chiro.wav" in f]

    if not os.path.exists(args.dest_dir) and not args.do_fake:
        os.mkdir(args.dest_dir)

    for f in sorted(files):
        print("Processing %s..." % f)
        fi = os.path.join(args.source_dir, f)
        f_name, f_ext = os.path.splitext(f)
        fo_0 = os.path.join(args.dest_dir, "%s_0_%%05d_000%s" % (f_name, f_ext))
        fo_1 = os.path.join(args.dest_dir, "%s_1_%%05d_000%s" % (f_name, f_ext))
        duration = float(subprocess.check_output((args.executable_ffprobe, "-v", "error", "-show_entries",
                                                  "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fi)))
        if args.do_fake:
            print("\tDetected duration: %f seconds" % duration)
            print("\tWould split it in chunks of %d seconds, giving pairs of files like %s/%s"
                  "" % (args.chunk_size, fo_0 % 0, fo_1 % 0))
        else:
            for s in range(0, math.ceil(duration), args.chunk_size):
                subprocess.call((args.executable_ffmpeg, "-v", "error", "-ss", "%d" % s, "-t", "%d" % args.chunk_size,
                                 "-i", fi, "-map_channel", "0.0.0", fo_0 % s, "-map_channel", "0.0.1", fo_1 % s))
        print("Done\n")


if __name__ == "__main__":
    main()
