#
#
#	Client Class for Python Client
#		This class will handle creating initiating requests to servers
#
#


from SocketChannel import SocketChannel, SocketChannelFactory
import comm_pb2
from comm_pb2 import Request
import struct, random, sys, os

class Client():
	def __init__(self):
		self.channelFactory = SocketChannelFactory()
  
	def executeOperation(self, option, host, port, param):
		if option == "photoCreateRequest":
			#Create a request for sending an image to server
			request = self.preparePhotoCreateRequest(param)
			print "\n\tPreparing POST /photo request for server (" + str(host) + ":" + str(port) +")"
			response = self.send(host, port, request)
			self.printPhotoCreateRequest(response)
		elif option == "photoReadRequest":
			#Create a request for retreiving an image from server
			request = self.preparePhotoReadRequest(param)
			print "\n\tPreparing GET /photo request for server (" + str(host) + ":" + str(port) + ")"
			response = self.send(host, port, request)
			self.printPhotoReadRequest(response)

	def preparePhotoCreateRequest(self, param):
		request = Request()

		# set headers for the request
		header = request.header
		header.routing_id = comm_pb2.Header.JOBS
		# TODO: get system user id to put as originator, because originator is an int (should be string), should we?
		header.originator = 1 #1 for python client, 2 for cpp, 3 for java
		#header.tag = any string
		#header.time = epoch system time
		header.photoHeader.requestType = comm_pb2.PhotoHeader.write
		#header.photoHeader.lastModified
		#header.photoHeader.contentLength

		# set body for the request
		body = request.body
		photoPayload = body.photoPayload
		photoPayload.name = os.path.basename(param)
		# parse the file into a byte array
		with open(param, 'rb') as image:
			readImage = image.read()
			readImageByteArray = bytearray(readImage)
		#print "req: " + str(request)
		photoPayload.data = str(readImageByteArray)

		#finish preparing the request
		return request

	def preparePhotoReadRequest(self, param):
		request = Request()

		#set headers for the request
		header = request.header
		header.routing_id = comm_pb2.Header.JOBS
		header.originator = 1

		#set body for the request
		body = request.body
		photoPayload = body.photoPayload
		photoPayload.uuid = str(param)

		#finish preparing the request
		return request


	def printPhotoReadRequest(self, response):
		if (response != None):
			print "\n\t***** Response received from server *****\n"
			print "\t RoutingID \t-> " + str(response.header.routing_id)
			print "\t Originator \t->" + str(response.header.originator)
			print "\t Data \t->" + str(response.body.photoPayload.data)
		else:
			print "\n\t***** No response received from server *****\n"

	def printPhotoCreateRequest(self, response):
		if (response != None):
			print "\n\t***** Response received from server *****\n"
			print "\t RoutingID \t->\t" + str(response.header.routing_id)
			print "\t Originator \t->\t" + str(response.header.originator)
			print "\t Photo UUID \t->\t" + str(response.body.photoPayload.uuid)	
		else:
			print "\n\t***** No response received from server *****\n"
					  
	def send(self, host, port, request):
		self.channel = self.channelFactory.openChannel(host, port)
		while self.channel.connected:
			try:
				self.channel.write(request.SerializeToString())
				print "\tConnected to channel and written message."
				resp = Request()
				resp.ParseFromString(self.channel.read())
				return resp
			except:
				print "\tException occurred: " + str(sys.exc_info()[0])
			finally:
				self.channel.close()
