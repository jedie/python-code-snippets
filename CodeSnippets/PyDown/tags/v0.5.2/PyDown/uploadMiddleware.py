
import time
import sys


class UploadMonitor(object):

    def __init__(self, callback, requestObjectKey, threshold, environ):
        self._callback = callback
        self._requestObjectKey = requestObjectKey
        self._threshold = threshold
        self._environ = environ
        self._stream = environ['wsgi.input']

    def read(self, size=-1):
        #~ print "-"*79
        #~ for k,v in environ.iteritems(): print k,"\t",v
        #~ print "-"*79
        contentLength = int(self._environ['CONTENT_LENGTH'])
        #~ print "contentLength:", contentLength

        if not self._environ.get('CONTENT_TYPE', '').startswith('multipart'):
            return self._stream.read()

        request = self._environ[self._requestObjectKey]

        # Wird per JS beim abschicken des Formulars als GET Parameter eingefügt!
        filename = request.args.get("filename","undefined")

        callback = self._callback(request, self._environ, filename)
        callback.start(contentLength)

        blockSize = self._threshold
        pos = 0
        result = ""
        while True:
            if (contentLength-pos)<blockSize: # nur noch Rest lesen
                blockSize = contentLength-pos

            data = self._stream.read(blockSize)
            if not data:
                #~ print "fertig 1"
                break
            pos += len(data)

            callback.update(pos)

            #~ print "%s - %s - %s - %s" % (
                #~ len(data), blockSize, pos, contentLength
            #~ )
            result += data
            if pos>=contentLength:
                #~ print "fertig 2"
                break

        callback.finished()
        #~ print "fertig!"
        return result


class ProgressMiddleware(object):

    def __init__(self, app, callback, requestObjectKey, threshold=2048):
        self._application = app
        self._callback = callback
        self._threshold = threshold
        self._requestObjectKey = requestObjectKey

    def __call__(self, environ, start_response):
        monitor = UploadMonitor(
            self._callback, self._requestObjectKey, self._threshold, environ
        )
        environ['wsgi.input'] = monitor
        return self._application(environ, start_response)




