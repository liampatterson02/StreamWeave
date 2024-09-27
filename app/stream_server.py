import subprocess
from flask import Response, stream_with_context
import logging
from database import get_stream_by_id  # Added missing import

def streamlink_stream(stream_id):
    stream = get_stream_by_id(stream_id)
    if not stream:
        return Response('Stream not found', status=404)

    cmd = ['streamlink', stream.url, 'best', '-O']

    if stream.auth:
        # Assuming auth is in the format "username:password"
        username, password = stream.auth.split(':')
        cmd.extend(['--http-user', username, '--http-pass', password])

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def generate():
            while True:
                chunk = process.stdout.read(8192)
                if not chunk:
                    break
                yield chunk
            process.stdout.close()
            process.wait()

            # Log any stderr output after the process ends
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

