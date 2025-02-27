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

It will auto-detect the number of available channels in the recordings (typically, mono or stereo,
but it can handle more if needed), and output split files accordingly.

Optionally, it can also perform some simple renaming to generate fully compatible filenames (avoids the extra
rename step prior to splitting audio files).

Note: provided you install FFMPEG and define ffmpeg/ffprobe executable paths, the script shall work on Windows as well…

[1] http://vigienature.mnhn.fr/page/vigie-chiro

Example
=======

Take raw wav files from ./raw_wav dir, rename them for circuit 605, year 2015, pass 1, and output their split versions
in current directory:

   ubat_slicer.py -s ./raw_wav -d . -R -c 605 -y 2015 -p 1

Take raw wav files from ./raw_wav dir, which are already expanded (sampling rate set to 19.2KHz instead of real 192KHz),
rename them for circuit 605, year 2017, pass 3, and output their split versions in current directory:

   ubat_slicer.py -s ./raw_wav -d . --speed-factor 10 -R -c 605 -y 2017 -p 3
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

    parser.add_argument("--speed-factor", dest="speed_fac", default=1, type=int,
            help="Speed factor (some recorders directly save audio files with reported low sampling rate, "
                 "which allows to play them back in time expanded way easily, "
                 "e.g. reporting 60 minutes at 19.2KHz instead of 6 minutes at 192 KHz)")

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
                print("Would rename '%s' to '%s' (new name does already exist: %r)" % (fi, fo, os.path.exists(fo)))
            elif os.path.exists(fo):
                print("NOT Renaming '%s' to '%s', as a file with target name already exists!" % (fi, fo))
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
        fo_pattern = os.path.join(args.dest_dir, f"{f_name}_%d_%05d_000{f_ext}")
        duration = float(subprocess.check_output((args.executable_ffprobe, "-v", "error", "-show_entries",
                                                  "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fi)))
        channels = int(subprocess.check_output((args.executable_ffprobe, "-v", "error", "-show_entries",
                                                "stream=channels", "-of", "default=noprint_wrappers=1:nokey=1", fi)))
        sample_rate = int(subprocess.check_output((args.executable_ffprobe, "-v", "error", "-show_entries",
                                                   "stream=sample_rate", "-of", "default=noprint_wrappers=1:nokey=1", fi)))
        duration /= args.speed_fac
        chunks_num = (math.ceil(duration) // args.chunk_size + int(bool(math.ceil(duration) % args.chunk_size)))

        if args.do_fake:
            print(f"\tDetected duration: {duration} seconds")
            print(
                f"\tWould split it in {chunks_num} chunks of {args.chunk_size} seconds, "
                f"giving sets of files like {', '.join((fo_pattern % (c, 0) for c in range(channels)))}"
            )
        else:
            # Write complex script into a temp text file, reduces the size of the ffmepg command.
            complex_script_path = os.path.join(args.dest_dir, "ffmpeg_complex_script.txt")
            with open(complex_script_path, "w") as script:
                # Set target sample rate (different from input one in case there is some non-unit speed factor).
                script.write(f"asetrate={sample_rate * args.speed_fac},\n")
                # Split channels into individual named streams '[Cn]'.
                script.write(f"channelsplit=channel_layout={channels}c{''.join([f'[C{c}]' for c in range(channels)])};\n")
                for c in range(channels):
                    # Split each channel into 'chunks_num' segments of 'chunk_size' length.
                    # NOTE: last timestamp (last chunk of audio) is implied,
                    #       which is why there is one less timestamp specified than streams generated.
                    script.write(f"[C{c}]asegment=timestamps={'|'.join([str(i * args.chunk_size) for i in range(1, chunks_num)])}")
                    # Capture all generated segments into named streams '[CnSn]'.
                    script.write("".join([f"[C{c}S{i}]" for i in range(chunks_num)]) + ";\n")
            # Generate all output files 'map' stream selectors and filenames.
            outputs_map = []
            outputs_files = []
            for c in range(channels):
                # Map selector of output stream from the complex filter (matches the one generated above, '[CnSn]').
                outputs_map += [f"[C{c}S{i}]" for i in range(chunks_num)]
                # And matching output filename.
                outputs_files += [fo_pattern % (c, i * args.chunk_size) for i in range(chunks_num)]
            # Process each input file in a single ffmpeg command.
            subprocess.call([args.executable_ffmpeg, "-v", "error", "-i", fi, "-filter_complex_script", complex_script_path] +
                            sum([["-map", m, fo] for m, fo in zip(outputs_map, outputs_files)], []))
            os.remove(complex_script_path)

        print("Done\n")


if __name__ == "__main__":
    main()
