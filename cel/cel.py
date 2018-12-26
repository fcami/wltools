#!/usr/bin/python3

# FLI (AF11), FLC (AF12), CEL (AF12) file reader

if __name__ != "__main__":
    sys.stderr.write('Not supported yet.')
    sys.exit(1)

import argparse
import sys
import binascii
import struct
import os

from enum import Enum, unique


FLI_TYPE='af11'
FLC_TYPE='af12'
CEL_TYPE=FLC_TYPE

FLI_FRAME_TYPE='f1fa'

@unique
class FliChunkType(Enum):
    FLI_COLOR256=4
    FLI_BRUN=15
    FLI_PSTAMP=18

# useful to decode DosDateTime
# in: integer
# out: two words
def bytes(i):
    return divmod(i, 0x100)


def decodeCelHeader(fd, fsize):

	fd.seek(0, 0)
	fli_size = struct.unpack('<I', fd.read(4))[0]
	if fli_size != fsize:
		# truncated FLI/FLC/CEL
		sys.stderr.write('Truncated file %s?' % args.celfile)
		raise RuntimeError
		sys.exit(1)
	print("File size: %s" % fli_size)
	fli_type1 = struct.unpack('<c', fd.read(1))[0]
	fli_type2 = struct.unpack('<c', fd.read(1))[0]
	fli_type = binascii.hexlify(fli_type2 + fli_type1)
	if fli_type == FLI_TYPE:
		print("FLI file detected.")
	elif fli_type == FLC_TYPE:
		print("FLC/CEL file detected.")
	fli_frames = struct.unpack('H', fd.read(2))[0]
	print("FLI frames: %s" % fli_frames)
	fli_width = struct.unpack('H', fd.read(2))[0]
	fli_height = struct.unpack('H', fd.read(2))[0]
	fli_depth = struct.unpack('H', fd.read(2))[0]
	if fli_depth != 8:
		# must be 8.
		sys.stderr.write('Error reading depth from header.')
		raise RuntimeError
	print("WxH@bpp: %sx%s@%s" % (fli_width, fli_height,fli_depth))
	fli_flags1 = struct.unpack('<c', fd.read(1))[0]
	fli_flags2 = struct.unpack('<c', fd.read(1))[0]
	fli_flags = binascii.hexlify(fli_flags2 + fli_flags1)
	if fli_flags != '0003':
		# must be '0003'.
		sys.stderr.write('Error reading flags from header.')
		raise RuntimeError
	print(fli_flags)

	fli_speed = struct.unpack('<I', fd.read(4))[0]
	# note: not enough data to double-check.
	if fli_type == FLI_TYPE:
		print("FLI delay: %s (1/70s)" % fli_speed)
	elif fli_type == FLC_TYPE:
		print("FLI delay: %sms" % fli_speed)

	# unused 2-byte offset after speed
	struct.unpack('>H', fd.read(2))[0]

	# DOS creation Date & Time, packed
	# http://msdn.microsoft.com/en-us/library/windows/desktop/ms724247%28v=vs.85%29.aspx
	# https://doxygen.reactos.org/d5/dac/dll_2win32_2kernel32_2client_2time_8c_source.html
	struct.unpack('<H', fd.read(2))[0]
	struct.unpack('<H', fd.read(2))[0]

	# S/N of creator
	struct.unpack('<I', fd.read(4))[0]

	# DOS update Date & Time, packed
	struct.unpack('<H', fd.read(2))[0]
	struct.unpack('<H', fd.read(2))[0]

	# S/N of updater program
	struct.unpack('<I', fd.read(4))[0]

	# aspectx, aspecty
	struct.unpack('<H', fd.read(2))[0]
	struct.unpack('<H', fd.read(2))[0]

	# jump over reserved area
	fd.seek(80, 0)

	if fli_type == FLI_TYPE:
		 print("FLI decoding not implemented.")
		 sys.exit(0)

	# FLC only.
	fli_offset1 = struct.unpack('<I', fd.read(4))[0]
	fli_offset2 = struct.unpack('<I', fd.read(4))[0]
	print("Offset to first frame: %s" % fli_offset1)
	print("Offset to second frame: %s" % fli_offset2)
	return (fli_offset1, fli_offset2)

def decodeCelFrame(fd, frameoffset):
	fd.seek(frameoffset, 0)
	header_size = struct.unpack('<I', fd.read(4))[0]
	print("Frame chunk size: %s" % header_size)
	chunk_id1 = struct.unpack('<c', fd.read(1))[0]
	chunk_id2 = struct.unpack('<c', fd.read(1))[0]
	chunk_id = binascii.hexlify(chunk_id2 + chunk_id1)
	if chunk_id != FLI_FRAME_TYPE:
		sys.stderr.write('Error reading flags from header.')
		raise RuntimeError
	fli_chunks = struct.unpack('H', fd.read(2))[0]
	print("Found %s chunks." % fli_chunks)

	# skip padding
	struct.unpack('<H', fd.read(2))[0]
	for i in range (0,3):
		struct.unpack('<H', fd.read(2))[0]

	for i in range(0, int(fli_chunks)):
		#readChunk()
		chunk_size = struct.unpack('<I', fd.read(4))[0]
		chunk_type = struct.unpack('<H', fd.read(2))[0]
		for cktype in list(FliChunkType):
			if chunk_type == cktype.value:
				print("Found %s chunk of size %s" % (cktype.name, chunk_size))
		fd.seek(chunk_size-6, 1)


def main():
    here = sys.path[0]
    parser = argparse.ArgumentParser(
            description='Read CEL files.')
    parser.add_argument('-f', action="store",
            dest="celfile", type=str)
    args=parser.parse_args()
    if args.celfile==None:
        sys.stderr.write('Error: specify CEL file to read')
        sys.exit(1)
    try:
        fsize = os.path.getsize(args.celfile)
        with open(args.celfile, 'rb') as fd:
            (fli_offset1, fli_offset2) = decodeCelHeader(fd, fsize)
            decodeCelFrame(fd, fli_offset1)
    except:
        sys.stderr.write('Could not read CEL file.')
        sys.exit(1)
    #size = int(binascii.hexlify(fli_size), 16)

if __name__ == "__main__":
    main()
