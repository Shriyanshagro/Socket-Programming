import socket				   # Import socket module
import os
import commands
import thread
import time

# global connection
connection =1

def client_script(threadName, delay):
	global connection
	s = socket.socket()			 # Create a socket object
	host = "127.0.0.1"	 # Get local machine name
	port = 22281				   # Reserve a port for your service.
	# port = 60000
	s.connect((host, port))

	# with open('received_file', 'wb') as f:
	#	 print 'file opened'
	while True:
			# s.send("Hello server!")
			# print('receiving data...')
			if connection == 0:
				break

			command = raw_input("PersonA >>")

			if command == "q":
				s.send(command)
				data = s.recv(1024)
				if data:
					print  data
				break

			elif command == 'd':
				s.send(command)
				arg = raw_input("Which protocol do ypu wanna choose(TCP/UDP) ??")
				s.send(arg)
				filename = raw_input("which file ? ")
				s.send(filename)
				filesize = s.recv(1024)
				
				if arg == "TCP":
					with open(filename, 'wb') as f:
						data = s.recv(1024)
						length = len(data)
						while filesize > length and data!="send":
							if data:
								f.write(data)		 # write data to a file
								print "data packets recieving..."
							data = s.recv(1024)
							length += len(data)

				
				elif arg == "UDP":
					with open(filename, 'wb') as f:
						data,addr = s.recvfrom(1024)
						length = len(data)
						while filesize > length and data!="send":
							if data:
								f.write(data)		 # write data to a file
								print "data packets recieving..."
							data,addr = s.recvfrom(1024)
							length += len(data)
							
				f.close()
				print "done"
				checksum = commands.getoutput("md5sum "+filename)
						# print "checksum matched"
				data = s.recv(1024)
				if data == checksum:
					print "File Successfully downloaded"
					print checksum
					s.send("0")
					timestamp = s.recv(1024)
					print "filesize =",filesize,"timestamp = ",timestamp
				else:
					print "File can't be Successfully downloaded,try once again"
					s.send("1")

			elif command == 'p':
				s.send(command)
				data = s.recv(1024)
				if data:
					print  '<< PersonB >> '
					print (data)

			elif command == "get":
				arg = raw_input("Give me the argument:")
				s.send(command)
				s.send(arg)
				if arg == "long":
					s.send(command)
					s.send(arg)
					data = s.recv(1024)
					print data
				elif arg == "short":
					start = raw_input("starttimestamp:(YYYYMMDD)")
					end = raw_input("endtimestamp:(YYYYMMDD)")
					s.send(start)
					s.send(end)
					# print 'req send'
					data = s.recv(1024)
					if data:
						data = data.split()
						length = len(data)
						for i in range(length):
							output = commands.getoutput("ls -l "+data[i])
							print output
					else:
						print "can't reach to server"
				else:
					
					print "Sorry . Gove me correct argument"
		
			elif command == "hash":
				arg = raw_input("Give me the argument:")
				s.send(command)
				s.send(arg)
				if arg == "verify":
					filename = raw_input("which file ? ")
					s.send(filename)
					checksum = s.recv(1024)
					last_modified = s.recv(1024)
					print "checksum = ",checksum,"last_modified =",last_modified
				elif arg=="checkall":
					data = ""
					while data != "done":
						data = s.recv(1024)
						print data
				else:
					print "Sorry . Gove me correct argument"
						
			else :
				print "wrong input given"

	print "bye"
	connection = 0
	s.close()
	return

def server_script(threadName, delay):
	global connection
	port = 60023					# Reserve a port for your service.
	# port = 60018
	s = socket.socket()			 # Create a socket object
	host = "127.0.0.1"	 # Get local machine name
	s.bind((host, port))			# Bind to the port
	s.listen(5)					 # Now wait for client connection.

	print 'Server listening....'
	data =""
	conn, addr = s.accept()	 # Establish connection with client.
	print 'Got connection from', addr

	try:
	   thread.start_new_thread( client_script, ("Thread-2", 4, ) )
	except:
	   print "Error: unable to start client"


	while True:

		if connection ==0:
			break

		if data == "q" :
			conn.send("connection closed")
			break

		elif data == "d":
				# conn.send("File name??")
				arg = conn.recv(1024)
				filename = conn.recv(1024)
				f = open(filename,'rb')
				filesize = commands.getoutput("ls -l "+filename+" | awk '{print $5}'")
				conn.send(filesize)
				# time.sleep(1)
				
				if arg == "TCP":
					l = f.read(1024)
					length = len(l)
					while filesize > length and l:
					   conn.send(l)
					   print 'sending data packets... '
					   l = f.read(1024)
					   length += len(l)
				
				elif arg == "UDP":
					l = f.read(1024)
					length = len(l)
					while filesize > length and l:
					   sent  = conn.sendto(l,addr)
					   print 'sending data packets... '
					   l = f.read(1024)
					   length += len(l)
					
				f.close()
				conn.send("send")
				checksum = commands.getoutput("md5sum "+filename)
				print "done"
				conn.send(checksum)
				data = conn.recv(1024)
				if data == "0":
					timestamp = commands.getoutput("ls -l "+filename+" | awk '{print $6,$7,$8}'")
					conn.send(timestamp)
					print "file Successfully send"
				else:
					print "error in sending file"

		elif data == "p" :
			output = commands.getoutput("ls")
			output = str(output)
			# repr is used for conersion into string
			conn.send(output)
			# print "ls"


		elif data == "get":
			arg = conn.recv(1024)
			# print "entered ",arg
			if arg == "long":
				output = commands.getoutput("ls -l")
				conn.send(output)
			elif arg == "short":
				# print " arg = ",arg
				start = conn.recv(1024)
				end = conn.recv(1024)
				# print "req recv"
				output = commands.getoutput("find * -newermt "+start+" \! -newermt "+end)
				# print len(output),output
				# output = output.split()
				# print len(output),output
				# output1 = commands.getoutput("echo "+output+"| sed -e 's/\n/ /'g ")
				# output2 = commands.getoutput("ls -l "+output)
				# print "req recv2",output1
				conn.send(output)
		
		elif data == "hash":
			arg = conn.recv(1024)
			if arg == "verify":
				filename = conn.recv(1024)
				checksum = commands.getoutput("md5sum "+filename)
				last_modified = commands.getoutput("ls -l "+filename+" |awk '{print $6,$7,$8}'")
				conn.send(checksum)
				conn.send(last_modified)
			elif arg == "checkall":
				files = commands.getoutput("ls")
				# print files
				files = files.split("\n")
				# print files,len(files)
				output = []
				for i in range(len(files)):
					# print files[i]
					output = commands.getoutput("md5sum "+files[i]
					+";ls -l "+files[i]+" |awk '{print $6,$7,$8}'"
					)
					# print output
					conn.send(output)
				conn.send("done")
		# for new requests
		data = conn.recv(1024)
		# sprint 'PerosonB >>', data


	print('Successfully conversation finished')
	conn.close()
	print('connection closed')
	connection = 0
	return

print "input 'p' for list all shared files of client "
print "input 'd' for downloading from shared files of client "
print "input 'q' for stop the server"
print "input 'get' following with arguments 'long or short' to get indexget "
print "input 'hash' follwing with arguments 'verify or checkall' to get changes in file"

try:
   thread.start_new_thread( server_script, ("Thread-1",2 ) )
except:
   print "Error: unable to start thread"


while connection ==1:
	pass
