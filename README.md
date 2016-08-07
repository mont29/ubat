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
