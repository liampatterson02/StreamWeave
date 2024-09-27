from database import get_streams
from flask import url_for

def generate_m3u():
    streams = get_streams()
    m3u_lines = ['#EXTM3U']
    for stream in streams:
        stream_url = url_for('stream', stream_id=stream.id, _external=True)
        m3u_lines.append(f'#EXTINF:-1,{stream.name}')
        m3u_lines.append(stream_url)
    return '\n'.join(m3u_lines)
