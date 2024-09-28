import subprocess
from flask import Response, stream_with_context, request, abort
import logging
from database import get_stream_by_id
import threading
import queue
import time

def streamlink_stream(stream_id):
    stream = get_stream_by_id(stream_id)
    if not stream:
        return Response('Stream not found', status=404)

    cmd = ['streamlink', stream.url, 'best', '-O']

    if stream.auth:
        # Assuming auth is in the format "username:password"
        # Adjust to handle plugin-specific authentication below
        pass  # We'll modify this in the next section

    # Include any additional parameters
    if stream.params:
        cmd.extend(stream.params.split())

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

        def generate():
            try:
                while True:
                    chunk = process.stdout.read(8192)
                    if not chunk:
                        break
                    yield chunk
                    # If client disconnected, terminate the subprocess
                    if request.environ.get('wsgi.input').closed:
                        break
                process.stdout.close()
            except GeneratorExit:
                pass
            except Exception as e:
                logging.exception("Error in streaming generator")
            finally:
                process.terminate()
                process.wait()
                stderr = process.stderr.read()
                if stderr:
                    logging.error(stderr.decode())
                process.stderr.close()

        return Response(
            stream_with_context(generate()),
            mimetype='video/mp2t',
            direct_passthrough=True,
        )
    except Exception as e:
        logging.exception("An error occurred while streaming")
        return Response(f'Error starting stream: {str(e)}', status=500)

