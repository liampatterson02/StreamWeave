import subprocess
from flask import Response, stream_with_context
import logging
from database import get_stream_by_id
import shlex

ALLOWED_PARAMS = {
    '--bbciplayer-username',
    '--bbciplayer-password',
    # Add other allowed parameters here
}

def validate_params(params_str):
    tokens = shlex.split(params_str)
    validated_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith('--'):
            if token not in ALLOWED_PARAMS:
                raise ValueError(f"Parameter {token} is not allowed.")
            # Ensure the parameter has an associated value
            if i + 1 >= len(tokens) or tokens[i + 1].startswith('--'):
                raise ValueError(f"Parameter {token} requires a value.")
            validated_tokens.extend([token, tokens[i + 1]])
            i += 2
        else:
            validated_tokens.append(token)
            i += 1
    return validated_tokens

def streamlink_stream(stream_id):
    stream = get_stream_by_id(stream_id)
    if not stream:
        return Response('Stream not found', status=404)

    cmd = ['streamlink', stream.url, 'best', '-O']

    if stream.params:
        try:
            additional_params = validate_params(stream.params)
            cmd.extend(additional_params)
        except ValueError as e:
            logging.error(str(e))
            return Response(str(e), status=400)

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def generate():
            try:
                while True:
                    chunk = process.stdout.read(8192)
                    if not chunk:
                        break
                    yield chunk
            except GeneratorExit:
                # Client disconnected
                pass
            except Exception as e:
                logging.exception("Error in streaming generator")
            finally:
                process.terminate()
                process.wait()
                stderr = process.stderr.read()
                if stderr:
                    logging.error(stderr.decode())
                process.stdout.close()
                process.stderr.close()

        return Response(
            stream_with_context(generate()),
            mimetype='video/mp2t',
            direct_passthrough=True,
        )
    except Exception as e:
        logging.exception("An error occurred while streaming")
        return Response(f'Error starting stream: {str(e)}', status=500)

