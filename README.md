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

Take raw wav files from ./raw_wav dir, rename them for circuit 601, year 2015, pass 1, and output their split versions
in current directory:

   ubat_slicer.py -s ./raw_wav -d . -R -c 601 -y 2015 -p 1

Take raw wav files from ./raw_wav dir, which are already expanded (sampling rate set to 19.2KHz instead of real 192KHz),
rename them for circuit 601, year 2017, pass 3, and output their split versions in current directory:

   ubat_slicer.py -s ./raw_wav -d . --speed-factor 10 -R -c 601 -y 2017 -p 3
