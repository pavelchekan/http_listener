from argparse import ArgumentParser
import io
import sys
import wave

from aiohttp import web
import aiobotocore
from pydub import AudioSegment

S3 = {
    'ID': 'AKIAISGPJ76Y4DIMTI5Q',
    'Key': 'ZyFvsXAR8URihdmiTuZ5jNvuCV+5u6qWQVU/AufY',
    'Bucket': 'uar-patrick-code-test',
    'Subdir': 'cdt-10302018a',
    'Host': 's3.us-east-2.amazonaws.com'
}


async def handle(request):
    auth = request.headers.get('Authorization', '')
    if auth != 'UAR-2017':
        return web.Response(status=401)
    session = aiobotocore.get_session(loop=request.loop)
    async with session.create_client('s3', region_name='us-east-2',
                                     aws_secret_access_key=S3['Key'],
                                     aws_access_key_id=S3['ID']) as client:
        if request.rel_url.path == '/wav-info':
            filename = request.rel_url.query['wavkey']
            filekey = S3['Subdir'] + '/' + filename
            response = await client.get_object(Bucket=S3['Bucket'], Key=filekey)

            async with response['Body'] as stream:
                in_bytes = await stream.read()
            tmp = io.BytesIO(in_bytes)

            wave_file = wave.open(tmp, 'r')
            resp = {
                "channel_count": wave_file.getnchannels(),
                "sample_rate": wave_file.getframerate(),
                "execution_time": round(wave_file.getnframes() / float(wave_file.getframerate()), 1)
            }
            return web.json_response(resp)
        elif request.rel_url.path == '/mp3-to-wav':
            wavname = request.rel_url.query['wavkey']
            mp3name = request.rel_url.query['mp3key']
            mp3key = S3['Subdir'] + '/' + mp3name
            wavkey = S3['Subdir'] + '/' + wavname
            response = await client.get_object(Bucket=S3['Bucket'], Key=mp3key)
            async with response['Body'] as stream:
                in_bytes = await stream.read()
            tmp = io.BytesIO(in_bytes)
            sound = AudioSegment.from_file(tmp, format="mp3")
            out_file = io.BytesIO()
            sound.export(out_file, format="wav")
            out_file.seek(0)
            await client.put_object(Bucket=S3['Bucket'], Key=wavkey, Body=out_file)
            out_file.seek(0)
            wave_file = wave.open(out_file, 'r')
            resp = {
                "file_size": sys.getsizeof(out_file),
                "execution_time": round(wave_file.getnframes() / float(wave_file.getframerate()), 1)
            }
            return web.json_response(resp)


def main(argv):
    arg_parser = ArgumentParser("listener")

    arg_parser.add_argument(
        "-p", "--port",
        help="TCP/IP port to serve on (default: %(default)r)",
        type=int,
        default="8089"
    )
    args = arg_parser.parse_args(argv)

    app = web.Application()
    app.add_routes([web.get('/wav-info', handle),
                    web.get('/mp3-to-wav', handle)])

    web.run_app(app, host='localhost', port=args.port)


if __name__ == "__main__":
    main(sys.argv[1:])
