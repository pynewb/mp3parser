#!/usr/bin/env python

'''mp3parser

MP3 parser and writer. Whereas I build an event-based parser (a la SAX) in mp3info, this builds a structure (a la DOM)
and provides a writer class to persist changes.
'''

import logging
import struct

FRAME_HEADER_SIZE = 10
HEADER_SIZE = 10

HEADER_SIZE_OFFSET = 6

if __name__ == '__main__':
	logging.basicConfig(filename='mp3parser.log', level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)

class ID3v2Frame(object):
	'''ID3v2 frame
	
	Frames currently parse themselves, whereas headers and frame headers
	are parsed externally.  For that reason, frames also re-constitute
	themselves
	'''
	
	def __init__(self, frame_header, frame_bytes):
		self.frame_header = frame_header
		self.frame_bytes = frame_bytes

	def __str__(self):
		return 'frame_header: {0} frame_bytes: {1}'.format(self.frame_header, repr(self.frame_bytes))

	def to_bytes(self):
		return self.frame_bytes

	def to_string(self, max_bytes=None):
		if max_bytes is None:
			return 'frame_header: {0} frame_bytes: {1}'.format(self.frame_header, repr(self.frame_bytes))
			
		return 'frame_header: {{{0}}} frame_bytes: {1} len: {2}'.format(self.frame_header, repr(self.frame_bytes[:int(max_bytes)]), len(self.frame_bytes))
		
class ID3v2FrameAttachedPicture(ID3v2Frame):
	'''ID3v2 attached picture frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FrameAttachedPicture, self).__init__(frame_header, frame_bytes)

		self.text_encoding = struct.unpack("B", frame_bytes[0])[0]
		LOGGER.debug('text_encoding %d bytes %s', self.text_encoding, repr(frame_bytes[1:32]))
		nul_index = frame_bytes.find('\x00', 1)
		self.mime_type = frame_bytes[1:nul_index]
		self.picture_type = struct.unpack("B", frame_bytes[nul_index + 1])[0]
		
		if self.text_encoding == 1:
			decription, self.picture_data = frame_bytes[nul_index + 2:].split('\x00\x00', 1)
			self.description = description.decode('utf-16')
		else:
			self.description, self.picture_data = frame_bytes[nul_index + 2:].split('\x00', 1)

	def __str__(self):
		return super(ID3v2FrameAttachedPicture, self).__str__() + ' text_encoding: {0} mime_type: {1} picture_type: {2} description: {3} picture_data: {4}'.format(self.text_encoding, self.mime_type, self.picture_type, self.description, repr(self.picture_data[:16]))

	def to_string(self, max_bytes=None):
		return super(ID3v2FrameAttachedPicture, self).to_string(max_bytes) + ' text_encoding: {0} mime_type: {1} picture_type: {2} description: {3} picture_data: {4}'.format(self.text_encoding, self.mime_type, self.picture_type, self.description, repr(self.picture_data[:16]))
		
class ID3v2FrameComment(ID3v2Frame):
	'''ID3v2 comment frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FrameComment, self).__init__(frame_header, frame_bytes)

		self.text_encoding = struct.unpack("B", frame_bytes[0])[0]
		LOGGER.debug('text_encoding %d bytes %s', self.text_encoding, repr(frame_bytes[1:]))
		self.language = frame_bytes[1:4]
		if self.text_encoding == 1:
			short_content_descrip, the_actual_text = frame_bytes[4:].split('\x00\x00', 1)
			self.short_content_descrip = short_content_descrip.decode('utf-16')
			self.the_actual_text = the_actual_text.decode('utf-16')
		else:
			self.short_content_descrip, self.the_actual_text = frame_bytes[4:].split('\x00', 1)

	def __str__(self):
		return super(ID3v2FrameComment, self).__str__() + ' text_encoding: {0} language: {1} short_content_descrip: {2} the_actual_text: {3}'.format(self.text_encoding, self.language, self.short_content_descrip, self.the_actual_text)

	def to_string(self, max_bytes=None):
		return super(ID3v2FrameComment, self).to_string(max_bytes) + ' text_encoding: {0} language: {1} short_content_descrip: {2} the_actual_text: {3}'.format(self.text_encoding, self.language, self.short_content_descrip, self.the_actual_text)
		
class ID3v2FrameGeneralEncapsulatedObject(ID3v2Frame):
	'''ID3v2 general encapsulated object frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FrameGeneralEncapsulatedObject, self).__init__(frame_header, frame_bytes)

		self.text_encoding = struct.unpack("B", frame_bytes[0])[0]
		LOGGER.debug('text_encoding %d bytes %s', self.text_encoding, repr(frame_bytes[1:32]))
		nul_index = frame_bytes.find('\x00', 1)
		self.mime_type = frame_bytes[1:nul_index]
		
		if self.text_encoding == 1:
			filename, content_description, self.encapsulated_object = frame_bytes[nul_index + 1:].split('\x00\x00', 2)
			self.filename = filename.decode('utf-16')
			self.content_description = content_description.decode('utf-16')
		else:
			self.filename, self.content_description, self.encapsulated_object = frame_bytes[nul_index + 1:].split('\x00', 2)

	def __str__(self):
		return super(ID3v2FrameGeneralEncapsulatedObject, self).__str__() + ' text_encoding: {0} mime_type: {1} filename: {2} content_description: {3} encapsulated_object: {4}'.format(self.text_encoding, self.mime_type, self.filename, self.content_description, repr(self.encapsulated_object[:16]))

	def to_string(self, max_bytes=None):
		return super(ID3v2FrameGeneralEncapsulatedObject, self).to_string(max_bytes) + ' text_encoding: {0} mime_type: {1} filename: {2} content_description: {3} encapsulated_object: {4}'.format(self.text_encoding, self.mime_type, self.filename, self.content_description, repr(self.encapsulated_object[:16]))
		
class ID3v2FrameMusicCDIdentifier(ID3v2Frame):
	'''ID3v2 music CD identifier frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FrameMusicCDIdentifier, self).__init__(frame_header, frame_bytes)

		self.cd_toc = frame_bytes

	def __str__(self):
		return super(ID3v2FrameMusicCDIdentifier, self).__str__() + ' cd_toc: {0} length: {1}'.format(repr(self.cd_toc[:16]), len(self.cd_toc))

	def to_string(self, max_bytes=None):
		return super(ID3v2FrameMusicCDIdentifier, self).to_string(max_bytes) + ' cd_toc: {0} length: {1}'.format(repr(self.cd_toc[:16]), len(self.cd_toc))
		
class ID3v2FramePrivate(ID3v2Frame):
	'''ID3v2 private frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FramePrivate, self).__init__(frame_header, frame_bytes)

		self.owner_identifier, self.the_private_data = frame_bytes.split('\x00', 1)

	def __str__(self):
		return super(ID3v2FramePrivate, self).__str__() + ' owner_identifier: {0} the_private_data: {1} length: {2}'.format(self.owner_identifier, repr(self.the_private_data[:16]), len(self.the_private_data))

	def to_string(self, max_bytes=None):
		return super(ID3v2FramePrivate, self).to_string(max_bytes) + ' owner_identifier: {0} the_private_data: {1} length: {2}'.format(self.owner_identifier, repr(self.the_private_data[:16]), len(self.the_private_data))
		
class ID3v2FrameTextInformation(ID3v2Frame):
	'''ID3v2 text information frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FrameTextInformation, self).__init__(frame_header, frame_bytes)

		self.text_encoding = struct.unpack("B", frame_bytes[0])[0]
		LOGGER.debug('text_encoding %d bytes %s', self.text_encoding, repr(frame_bytes[1:]))
		if self.text_encoding == 1:
			self.information = frame_bytes[1:].decode('utf-16')
		else:
			self.information = frame_bytes[1:]

	def __str__(self):
		return super(ID3v2FrameTextInformation, self).__str__() + ' text_encoding: {0} information: {1}'.format(self.text_encoding, self.information)

	def to_bytes(self):
		if self.text_encoding == 1:
			return '\x01' + self.information.encode('utf-16')
		return '\x00' + self.information

	def to_string(self, max_bytes=None):
		return super(ID3v2FrameTextInformation, self).to_string(max_bytes) + ' text_encoding: {0} information: {1}'.format(self.text_encoding, self.information)
		
class ID3v2FrameUserDefinedTextInformation(ID3v2Frame):
	'''ID3v2 user defined text information frame'''
	
	def __init__(self, frame_header, frame_bytes):
		super(ID3v2FrameTextInformation, self).__init__(frame_header, frame_bytes)

		self.text_encoding = struct.unpack("B", frame_bytes[0])[0]
		LOGGER.debug('text_encoding %d bytes %s', self.text_encoding, repr(frame_bytes[1:]))
		if self.text_encoding == 1:
			information = frame_bytes[1:].decode('utf-16')
			self.description, self.value = information.split(u'\u0000', 1)
		else:
			information = frame_bytes[1:]
			self.description, self.value = information.split('\x00', 1)

	def __str__(self):
		return super(ID3v2FrameUserDefinedTextInformation, self).__str__() + ' text_encoding: {0} description: {1} value: {2}'.format(self.text_encoding, self.description, self.value)

	def to_string(self, max_bytes=None):
		return super(ID3v2FrameUserDefinedTextInformation, self).to_string(max_bytes) + ' text_encoding: {0} description: {1} value: {2}'.format(self.text_encoding, self.description, self.value)
		
class ID3v2FrameHeader(object):
	'''ID3v2 frame header'''
	
	def __init__(self, frame_id, size, flags):
		self.frame_id = frame_id
		self.size = size
		self.flags = flags

	def __str__(self):
		return 'frame_id: {0} size: {1} flags: {2}'.format(self.frame_id, self.size, self.flags)

class ID3v2Header(object):
	'''ID3v2 tag header'''
	
	def __init__(self, unsynchronization, extended_header, size):
		self.unsynchronization = unsynchronization
		self.extended_header = extended_header
		self.size = size
	
	def __str__(self):
		return 'unsynchronization: {0} extended_header: {1} size: {2}'.format(self.unsynchronization, self.extended_header, self.size)

class MP3ParserError(Exception):
	'''Exceptions from the mp3 module'''
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class MP3File(object):
	'''Parsed contents of an MP3 file'''
	
	def __init__(self, header, frames=[], payload=None, path=None):
		self.header = header
		self.frames = frames
		self.payload = payload
		self.path = path

	def __str__(self):
		return 'header: {{{0}}}\nframes: [{1}]\npath: {2}'.format(self.header, ",\n".join(['{' + f.to_string(16) + '}' for f in self.frames]), self.path)

class MP3Parser(object):
	'''Parses an MP3 file'''
	
	@classmethod
	def parse_file(cls, path):
		with open(path, 'rb') as f:
			header_bytes = f.read(HEADER_SIZE)
			header = cls.parse_header(header_bytes)
			
			header_size = header.size + HEADER_SIZE
			LOGGER.debug('header_size: %d', header_size)

			frames = []
			
			LOGGER.debug('f.tell: %d', f.tell())
			while f.tell() + FRAME_HEADER_SIZE < header_size:
				frame_header_bytes = f.read(FRAME_HEADER_SIZE)
				frame_header = cls.parse_frame_header(frame_header_bytes)
				if frame_header is None:
					LOGGER.debug('no frame in frame_header_bytes: %s', repr(frame_header_bytes))
					break
				LOGGER.debug('frame_id: %s size: %d', frame_header.frame_id, frame_header.size)

				frame_bytes = f.read(frame_header.size)
				frame = cls.parse_frame(frame_header, frame_bytes)
				frames.append(frame)
				LOGGER.debug('f.tell: %d', f.tell())

			return MP3File(header, frames=frames, path=path)

	@classmethod
	def parse_frame(cls, frame_header, frame_bytes):
		if frame_header.frame_id in ('TALB', 'TBPM', 'TCOM', 'TCON', 'TCOP', 'TDAT', 'TDLY', 'TENC', 'TEXT', 'TFLT', 'TIME', 'TIT1', 'TIT2', 'TIT3', 'TKEY', 'TLAN', 'TLEN', 'TMED', 'TOAL', 'TOFN', 'TOLY', 'TOPE', 'TORY', 'TOWN', 'TPE1', 'TPE2', 'TPE3', 'TPE4', 'TPOS', 'TPUB', 'TRCK', 'TRDA', 'TRSN', 'TRSO', 'TSIZ', 'TSRC', 'TSSE', 'TYER'):
			return ID3v2FrameTextInformation(frame_header, frame_bytes)

		if frame_header.frame_id in ('TXXX'):
			return ID3v2FrameTextUserDefinedInformation(frame_header, frame_bytes)
		
		if frame_header.frame_id in ('COMM'):
			return ID3v2FrameComment(frame_header, frame_bytes)

		if frame_header.frame_id in ('PRIV'):
			return ID3v2FramePrivate(frame_header, frame_bytes)

		if frame_header.frame_id in ('APIC'):
			return ID3v2FrameAttachedPicture(frame_header, frame_bytes)

		if frame_header.frame_id in ('GEOB'):
			return ID3v2FrameGeneralEncapsulatedObject(frame_header, frame_bytes)

		if frame_header.frame_id in ('MCDI'):
			return ID3v2FrameMusicCDIdentifier(frame_header, frame_bytes)

		return ID3v2Frame(frame_header, frame_bytes)

	@classmethod
	def parse_frame_header(cls, frame_header_bytes):
		if len(frame_header_bytes) != FRAME_HEADER_SIZE:
			raise MP3ParserError('A frame header must be {0} bytes, not {1}'.format(FRAME_HEADER_SIZE, len(frame_header_bytes)))

		frame_id = frame_header_bytes[0:4]
		if frame_id == '\x00\x00\x00\x00':
			return None
		size = struct.unpack('>I', frame_header_bytes[4:8])[0]
		flags = struct.unpack('>H', frame_header_bytes[8:10])[0]
		
		#tag_alter_preservation = (flags & (1 << 15)) >> 15;
		#file_alter_preservation = (flags & (1 << 14)) >> 14;
		#read_only = (flags & (1 << 13)) >> 13;
		
		#compression = (flags & (1 << 7)) >> 7;
		#encryption = (flags & (1 << 6)) >> 6;
		#grouping_identity = (flags & (1 << 5)) >> 5;
		
		return ID3v2FrameHeader(frame_id, size, flags)

	@classmethod
	def parse_header(cls, header_bytes):
		if len(header_bytes) != HEADER_SIZE:
			raise MP3ParserError('The ID3v2 header must be {0} bytes, not {1}'.format(HEADER_SIZE, len(header_bytes)))

		if header_bytes[0:3] != 'ID3':
			raise MP3ParserError('The ID3v2 header identifier must be ID3, not {0}'.format(header_bytes[0:3]))
			
		if header_bytes[3:5] != '\x03\x00':
			raise MP3ParserError('The ID3v2 header version must be 3, not {0}'.format(header_bytes[3:5]))
			
		flags = struct.unpack('B', header_bytes[5:6])[0]
		unsynchronization = (flags & 0x80) >> 7
		if unsynchronization:
			raise MP3ParserError('This parser does not support unsynchronization')

		extended_header = (flags & 0x60) >> 6
		if extended_header:
			raise MP3ParserError('This parser does not support extended_header')

		size_bytes = struct.unpack('BBBB', header_bytes[6:10])
		size = ((size_bytes[0] * (1 << 21)) +
		       (size_bytes[1] * (1 << 14)) +
			   (size_bytes[2] * (1 << 7)) +
			   size_bytes[3])
		
		return ID3v2Header(unsynchronization, extended_header, size)

class MP3Writer(object):
	'''Writes an MP3 file'''

	@classmethod
	def get_header_bytes(cls, header):
		if header.unsynchronization:
			raise MP3ParserError('This writer does not support unsynchronization')

		if header.extended_header:
			raise MP3ParserError('This writer does not support extended_header')

		flags = (header.unsynchronization << 7) | (header.extended_header << 6)
		return 'ID3' + '\x03\x00' + struct.pack('B', flags) + cls.get_header_size_bytes(header.size)
		
	@classmethod
	def get_header_size_bytes(cls, header_size):
		header_size_bytes0 = (header_size & 0x0fe00000) >> 21
		header_size_bytes1 = (header_size & 0x001fc000) >> 14
		header_size_bytes2 = (header_size & 0x00003f80) >> 7
		header_size_bytes3 = (header_size & 0x0000007f)
		return struct.pack('BBBB', header_size_bytes0, header_size_bytes1, header_size_bytes2, header_size_bytes3)

	@classmethod
	def get_frame_header_bytes(cls, frame_header, frame_size):
		return frame_header.frame_id + struct.pack('>I', frame_size) + struct.pack('>H', frame_header.flags)
	
	@classmethod
	def get_frame_bytes(cls, frame):
		return frame.to_bytes()

	@classmethod
	def write_file(cls, path, mp3file):
		with open(path, 'wb') as f:
			header_bytes = cls.get_header_bytes(mp3file.header)
			f.write(header_bytes)
			
			for frame in mp3file.frames:
				frame_bytes = cls.get_frame_bytes(frame)
				frame_header_bytes = cls.get_frame_header_bytes(frame.frame_header, len(frame_bytes))
				f.write(frame_header_bytes)
				f.write(frame_bytes)
			
			if f.tell() > mp3file.header.size + HEADER_SIZE:
				LOGGER.debug('resize: wrote %d bytes but size was %d', f.tell(), mp3file.header.size + HEADER_SIZE)
				header_size = f.tell() - HEADER_SIZE
				f.seek(HEADER_SIZE_OFFSET)
				f.write(cls.get_header_size_bytes(header_size))
				f.seek(header_size + HEADER_SIZE)
			elif f.tell() < mp3file.header.size + HEADER_SIZE:
				LOGGER.debug('pad: wrote %d bytes but size was %d', f.tell(), mp3file.header.size + HEADER_SIZE)
				f.write('\x00' * (mp3file.header.size + HEADER_SIZE - f.tell()))
			
			if mp3file.payload is not None:
				f.write(mp3file.payload)
			else:
				with open(mp3file.path, 'rb') as ff:
					ff.seek(mp3file.header.size + HEADER_SIZE)
					f.write(ff.read())

if __name__ == '__main__':
	'''The main "routine"
	
	This has two usage patterns to apply the parser as a utility.  The first form,
	with one argument, displays the parsed ID3v2 header of the file specified by
	that argument.  The second form, with four arguments, writes a new copy of
	the file specified by the first argument as the file specified by the second
	argument, replacing the (text) frame information as specified by the frame-id
	and frame-information third and fourth arguments.
	'''

	import os.path
	import sys

	if len(sys.argv) not in (2, 5):
		print >>sys.stderr, 'usage: {0} mp3-file [new-mp3-file frame-id frame-information]'.format(sys.argv[0])
		sys.exit(1)

	path = sys.argv[1]
	file = MP3Parser.parse_file(path)
	
	if len(sys.argv) == 2:
		print file

	elif len(sys.argv) == 5:
		frame_id = sys.argv[3]
		information = sys.argv[4]
		for frame in file.frames:
			if frame.frame_header.frame_id == frame_id:
				print 'Replace {0} with {1}'.format(frame.information, information)
				if frame.text_encoding == 1:
					frame.information = unicode(information)
				else:
					frame.information = str(information)

		new_path = sys.argv[2]
		print new_path
		MP3Writer.write_file(new_path, file)
